import boto3
import datetime
import json
import logging
import os

from botocore.exceptions import ClientError


def _get_arn(lookup_token):
    if lookup_token is not None:
        client = boto3.client('dynamodb')
        row = client.get_item(TableName=os.getenv('AUTH_TABLE', 'role_perms'),
                              Key={'auth_token': {'S': lookup_token}})
        if row is not None:
            return row['Item']['role_arn']['S']
        else:
            return None
    else:
        return None


def _get_credentials(auth_token):
    arn = None
    if auth_token is not None:
        arn = _get_arn(auth_token)

    if arn is not None:
        sts_client = boto3.client('sts')
        credentials = sts_client.assume_role(RoleArn=arn,
                                             DurationSeconds=os.getenv('DEFAULT_DURATION', 900),
                                             RoleSessionName=auth_token)

        # Calculating 300 seconds (5 minutes) short of the expiration for allowing caching.
        delta_in_seconds = int(credentials['Credentials']['Expiration'].strftime("%s")) - \
                int(datetime.datetime.utcnow().strftime("%s")) - 300

        ecs_payload = {
            'AccessKeyId': credentials['Credentials']['AccessKeyId'],
            'SecretAccessKey': credentials['Credentials']['SecretAccessKey'],
            'Token': credentials['Credentials']['SessionToken'],
            'Expiration': credentials['Credentials']['Expiration'].isoformat()
        }
        return ecs_payload, delta_in_seconds
    else:
        return None, None


def handler(event, context):

    logger = logging.getLogger(__name__)

    to_return = {
        'headers': {'Content-Type': 'application/json'}
    }

    try:
        if event and 'Authorization' in event['headers']:
            auth_token = event['headers']['Authorization']

            credentials, max_age = _get_credentials(auth_token)
            if max_age is not None and max_age > 0:
                to_return['headers']['Cache-control'] = ('max-age=' + str(max_age))
            else:
                to_return['headers']['Cache-control'] = 'no-cache'

            if credentials is not None:
                to_return['statusCode'] = 200
                data = credentials
            else:
                data = {
                    'output': 'Not Found',
                }
                to_return['statusCode'] = 404
        else:
            data = {
                'output': 'Not Authorized',
            }
            to_return['statusCode'] = 401

    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            logger.error("Table does not exist: %s" % e)
        else:
            logger.error("Unexpected error: %s" % e)
        data = {
            'output': 'Server Error',
            'timestamp': datetime.datetime.utcnow().isoformat()
        }
        to_return['statusCode'] = 503

    to_return['body'] = json.dumps(data)
    return to_return
