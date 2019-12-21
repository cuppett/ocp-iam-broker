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
        patchset = 'WwogICAgewogICAgICAgICJvcCI6ICJhZGQiLAogICAgICAgICJwYXRoIjogIi9zcGVjL2NvbnRhaW5lcnMvMC9lbnYiLAogI' \
                   'CAgICAgICJ2YWx1ZSI6IFsKICAgICAgICAgICAgewogICAgICAgICAgICAgICAgIm5hbWUiOiAiQVdTX0NPTlRBSU5FUl9DUk' \
                   'VERU5USUFMU19GVUxMX1VSSSIsCiAgICAgICAgICAgICAgICAidmFsdWUiOiAiaHR0cDovLzEyNy4wLjAuMTo1MzA4MC8iCiA' \
                   'gICAgICAgICAgIH0sCiAgICAgICAgICAgIHsKICAgICAgICAgICAgICAgICJuYW1lIjogIkFXU19DT05UQUlORVJfQVVUSE9S' \
                   'SVpBVElPTl9UT0tFTiIsCiAgICAgICAgICAgICAgICAidmFsdWUiOiAiOTY5MkVENEI3OTJCNDkwOThCMDY3MEQxMDc5NDhBM' \
                   'UY4RDZBODdERiIKICAgICAgICAgICAgfQogICAgICAgIF0KICAgIH0KXQ=='
    else:
        patchset = 'W10K'

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
