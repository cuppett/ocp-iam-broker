import json
import logging


def handler(event, context):

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    body = json.loads(event['body'])

    namespace = body['request']['namespace']
    operation = body['request']['operation']

    logger.debug('Namespace: ' + namespace + ' Operation: ' + operation)

    if operation == 'CREATE':
        patchset = 'W3sib3AiOiAiYWRkIiwgInBhdGgiOiAiL3NwZWMvY29udGFpbmVycy8wL2VudiIsICJ2YWx1ZSI6IFt7Im5hbWUiOiAiQV' \
                   'dTX0NPTlRBSU5FUl9DUkVERU5USUFMU19GVUxMX1VSSSIsCiAgICAgICAgICAgICAgICAidmFsdWUiOiAiaHR0cDovLzEy' \
                   'Ny4wLjAuMTo1MzA4MC8iCiAgICAgICAgICAgIH0sCiAgICAgICAgICAgIHsKICAgICAgICAgICAgICAgICJuYW1lIjogIk' \
                   'FXU19DT05UQUlORVJfQVVUSE9SSVpBVElPTl9UT0tFTiIsCiAgICAgICAgICAgICAgICAidmFsdWUiOiAiOTY5MkVENEI3O' \
                   'TJCNDkwOThCMDY3MEQxMDc5NDhBMUY4RDZBODdERiIKICAgICAgICAgICAgfQogICAgICAgIF0KICAgIH0KXQ=='
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
