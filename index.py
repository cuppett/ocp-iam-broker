import broker
import boto3
import logging
import os
import webhook

logger = logging.getLogger()
logger.setLevel(logging.DEBUG if os.getenv('APP_DEBUG', '') == 'true' else logging.INFO)

if os.getenv('AWS_REGION'):
    boto3.setup_default_session(region_name=os.getenv('AWS_REGION'))


def handler(event, context):

    logger.debug(event)
    to_return = None

    if event['httpMethod'] == 'GET':
        to_return = broker.handler(event, context)
    elif event['httpMethod'] == 'POST':
        to_return = webhook.handler(event, context)

    if to_return is None:
        to_return = {
            'headers': {'Content-Type': 'application/json'},
            'statusCode': 503,
            'body': {'data': {'output': 'Invalid invocation'}}
        }

    return to_return


if __name__ == "__main__":
    print(handler({'httpMethod': 'GET', 'headers': {'Authorization': os.getenv('AUTH_TOKEN')}}, None))
