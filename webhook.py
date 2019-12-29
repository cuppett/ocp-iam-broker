import base64
import boto3
import copy
import json
import jsonpatch
import logging
import os
import random
import string

from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.config.kube_config import _create_temp_file_with_content as create_temp_file

_EMPTY_PATCHSET = 'W10='

_logger = logging.getLogger()
_logger.setLevel(logging.DEBUG if os.getenv('APP_DEBUG', '') == 'true' else logging.INFO)


def _get_kubeconfig() -> None:
    """Retrieves the required kubeconfig from SSM Parameter Store. This function must have the ability to decrypt
    via the key. The default KMS is easy, a customer key will require extra permissions for the role."""
    ssm_client = boto3.client('ssm')
    kubeconfig = ssm_client.get_parameter(Name=os.getenv('KUBECONFIG', 'WEBHOOK_KUBECONFIG'), WithDecryption=True)
    filename = create_temp_file(kubeconfig)
    config.load_kube_config(config_file=str(filename))


def _identify_target_arn(namespace: string, serviceaccount: string) -> string:
    """Will lookup the target ARN in Kubernetes via an annotation on the ServiceAccount.
    If none is found, or there is an error, will return None."""

    # Identifying the annotation to find. Using the default to match the EKS webhook
    arn_annotation = os.getenv('ARN_ANNOTATION', 'eks.amazonaws.com/role-arn')

    # Retrieving the annotation
    try:
        v1 = client.CoreV1Api()
        resp = v1.read_namespaced_service_account(namespace, serviceaccount)
        if resp.metadata.annotations is not None and arn_annotation in resp.metadata.annotations:
            _logger.debug('Annotation found: ' + resp.metadata.annotations[arn_annotation])
            return resp.metadata.annotations[arn_annotation]
        else:
            _logger.debug('No annotation %s found for namespace %s and serviceaccount %s',
                          arn_annotation, namespace, serviceaccount)
            return None
    except ApiException as e:
        _logger.error("Unknown error trying to fetch serviceaccount: %s" % e)
        return None


def _delete_secret(namespace: string, name: string) -> None:
    try:
        v1 = client.CoreV1Api()
        v1.delete_namespaced_secret(name, namespace)
        _logger.info("Secret %s removed in namespace %s", name, namespace)
    except ApiException as e:
        _logger.error("Unknown error removing secret: %s" % e)


def _create_secret(namespace: string, auth_token: string) -> string:
    try:
        v1 = client.CoreV1Api()
        secret_name = 'broker-authorization-' + \
                      ''.join([random.choice(string.ascii_lowercase + string.digits) for n in range(32)])
        secret = {
            'apiVersion': 'v1',
            'kind': 'Secret',
            'metadata': {
                'name': secret_name,
                'namespace': namespace
            },
            'type': 'Opaque',
            'stringData': {
                'AWS_CONTAINER_AUTHORIZATION_TOKEN': auth_token
            }
        }
        resp = v1.create_namespaced_secret(namespace, secret)
        _logger.debug('Result of the call: %s', resp)
        return secret_name
    except ApiException as e:
        _logger.error("Unknown error generating secret: %s" % e)
        return None


def _get_allowed_arns(namespace: string, serviceaccount: string) -> []:
    """Looks up the allowed ARNs from DynamoDB. We ensure this """
    dynamo = boto3.client('dynamodb')
    row = dynamo.get_item(TableName=os.getenv('MAP_TABLE', 'mapped_roles'),
                          Key={'namespace': {'S': namespace}, 'service_account':  {'S': serviceaccount}})
    if row is not None:
        return row['Item']['allowed_roles']['SS']

    return None


def _insert_auth_row(auth_token: string, role_arn: string, secret_name: string, namespace: string,
                     service_account: string) -> None:
    dynamo = boto3.client('dynamodb')
    item = {
        'auth_token': {
            'S': auth_token
        },
        'namespace': {
            'S': namespace
        },
        'secret_name': {
            'S': secret_name
        },
        'role_arn': {
            'S': role_arn
        },
        'service_account': {
            'S': service_account
        }
    }
    dynamo.put_item(TableName=os.getenv('AUTH_TABLE', 'role_perms'), Item=item)


def _get_auth_secret(namespace: string, service_account: string) -> string:

    # Identify if there is a target ARN which is valid
    arn_list = _get_allowed_arns(namespace, service_account)
    target_arn = None
    if arn_list is not None and len(arn_list) > 0:
        _logger.debug('List of ARNs: %s', arn_list)
        target_arn = _identify_target_arn(namespace, service_account)
        _logger.debug('Target ARN: %s', target_arn)

    # Setting up Kubernetes and DynamoDB with the needed Secret & row
    if target_arn is not None and target_arn in arn_list:
        auth_token = ''.join([random.choice(string.letters + string.digits) for n in range(64)])
        secret_name = _create_secret(namespace, auth_token)

        # Insert the auth row into DynamoDB
        if secret_name is not None:
            try:
                _insert_auth_row(auth_token, target_arn, secret_name, namespace, service_account)
                return secret_name
            except Exception as e:
                _logger.error("Unknown error storing dynamoDB row: %s" % e)
                # Unwind and remove the Kubernetes secret
                _delete_secret(namespace, secret_name)

    return None


def _remove_auth_row(namespace: string, pod_name: string) -> None:
    """TODO: Need a way to identify this row, pod_name is not guaranteed to exist when using generated name."""
    pass


def _update_pod_spec(original: [], secret_name: string) -> []:
    new = copy.deepcopy(original)

    # Add the secret & proxy environment variable to all the existing containers
    for container in new['spec']['containers']:
        if 'env' not in container:
            container['env'] = []
        container['env'].append({
            'name': 'AWS_CONTAINER_CREDENTIALS_FULL_URI',
            'value': 'http://127.0.0.1:' + os.getenv('PROXY_PORT', '53080')
        })
        container['env'].append({
            'name': 'AWS_CONTAINER_AUTHORIZATION_TOKEN',
            'valueFrom': {'secretKeyRef': {'name': secret_name, 'key': 'AWS_CONTAINER_AUTHORIZATION_TOKEN'}}
        })
    # Adding the proxy container to the pod spec
    proxy_container = {
        'name': 'ocp-broker-proxy',
        'image': os.getenv('PROXY_IMAGE',
                           'image-registry.openshift-image-registry.svc:5000/ocp-iam-broker/ocp-broker-proxy'),
        'resources': {
            'requests': {
                'memory': os.getenv('PROXY_MEMORY_REQUESTS', '15Mi'),
                'cpu': os.getenv('PROXY_CPU_REQUESTS', '1m')
            },
            'limits': {
                'memory': os.getenv('PROXY_MEMORY_LIMITS', '32Mi'),
                'cpu': os.getenv('PROXY_CPU_LIMITS', '10m')
            }
        }
    }
    new['spec']['containers'].append(proxy_container)
    return new


def _generate_patchset(request_body: []) -> string:
    namespace = request_body['namespace']
    service_account = request_body['object']['spec']['serviceAccountName']
    auth_secret = _get_auth_secret(namespace, service_account)

    # If we have an identified auth_token
    if auth_secret is not None:
        # Creating actual patch for insertion into response
        new = _update_pod_spec(request_body['object'], auth_secret)
        patch = jsonpatch.JsonPatch.from_diff(request_body['object'], new)
        string_patch = patch.to_string()
        logging.debug('Patched Object: %s', string_patch)
        encodedBytes = base64.b64encode(string_patch.encode("utf-8"))
        encodedStr = str(encodedBytes, "utf-8")
        logging.debug('Encoded patch: %s', encodedStr)

        return encodedStr

    else:
        return _EMPTY_PATCHSET


def handler(event, context):
    body = json.loads(event['body'])
    patchset = _EMPTY_PATCHSET

    if body['request']['kind']['kind'] is 'Pod':
        _get_kubeconfig()
        namespace = body['request']['namespace']
        operation = body['request']['operation']

        _logger.debug('Namespace: ' + namespace + ' Operation: ' + operation)

        if operation == 'CREATE':
            patchset = _generate_patchset(body['request'])
        elif operation == 'DELETE':
            pod_name = body['request']['name']
            _remove_auth_row(namespace, pod_name)

    to_return = {
        'headers': {'Content-Type': 'application/json'},
        'statusCode': 200,
        'body': json.dumps({
            "apiVersion": body['apiVersion'],
            "kind": "AdmissionReview",
            "response": {
                "uid": body['request']['uid'],
                "allowed": True,
                "patchType": "JSONPatch",
                "patch": patchset
            }
        })
    }

    _logger.debug(to_return)

    return to_return
