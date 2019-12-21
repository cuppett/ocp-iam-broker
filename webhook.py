import json
import logging


def handler(event, context):

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    body = json.loads(event['body'])

    namespace = body['request']['namespace']
    operation = body['request']['operation']

    logger.debug('Namespace: ' + namespace + ' Operation: ' + operation)

    if operation == 'CREATE' and namespace == 'app1':
        patchset = 'WwogICAgewogICAgICAgICJvcCI6ICJhZGQiLAogICAgICAgICJwYXRoIjogIi9zcGVjL2NvbnRhaW5lcnMvMC9lbnYiLAog' \
                   'ICAgICAgICJ2YWx1ZSI6IFsKICAgICAgICAgICAgewogICAgICAgICAgICAgICAgIm5hbWUiOiAiQVdTX0NPTlRBSU5FUl9D' \
                   'UkVERU5USUFMU19GVUxMX1VSSSIsCiAgICAgICAgICAgICAgICAidmFsdWUiOiAiaHR0cDovLzEyNy4wLjAuMTo1MzA4MC8i' \
                   'CiAgICAgICAgICAgIH0sCiAgICAgICAgICAgIHsKICAgICAgICAgICAgICAgICJuYW1lIjogIkFXU19DT05UQUlORVJfQVVUS' \
                   'E9SSVpBVElPTl9UT0tFTiIsCiAgICAgICAgICAgICAgICAidmFsdWVGcm9tIjogewogICAgICAgICAgICAgICAgICAgICJzZW' \
                   'NyZXRLZXlSZWYiOiB7CiAgICAgICAgICAgICAgICAgICAgICAgICJuYW1lIjogImJyb2tlci1hdXRob3JpemF0aW9uLXhremt' \
                   'kZSIsCiAgICAgICAgICAgICAgICAgICAgICAgICJrZXkiOiAiQVdTX0NPTlRBSU5FUl9BVVRIT1JJWkFUSU9OX1RPS0VOIgog' \
                   'ICAgICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgfQogICAgICAgIF0KICAgIH0KXQ'
    else:
        patchset = 'W10='

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

    logger.debug(to_return)

    return to_return
