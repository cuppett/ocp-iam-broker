import broker
import logging
import os
import webhook

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


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
