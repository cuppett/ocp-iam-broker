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
        patchset = 'W3sgIm9wIjogImFkZCIsICJwYXRoIjogIi9zcGVjL2NvbnRhaW5lcnMvMC9lbnYiLCAidmFsdWUiOiBbeyAibmFtZSI6ICJ' \
                   'BV1NfQ09OVEFJTkVSX0NSRURFTlRJQUxTX0ZVTExfVVJJIiwgInZhbHVlIjogImh0dHA6Ly8xMjcuMC4wLjE6NTMwODAvIi' \
                   'B9LHsgIm5hbWUiOiAiQVdTX0NPTlRBSU5FUl9BVVRIT1JJWkFUSU9OX1RPS0VOIiwgInZhbHVlIjogIjk2OTJFRDRCNzkyQ' \
                   'jQ5MDk4QjA2NzBEMTA3OTQ4QTFGOEQ2QTg3REYiIH1dXQ=='
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
