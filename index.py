import boto3
import datetime
import json
import logging
import os

from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

if os.getenv('AWS_REGION'):
    boto3.setup_default_session(region_name=os.getenv('AWS_REGION'))


def get_arn(lookup_token):

    if lookup_token is not None:
        client = boto3.client('dynamodb')
        row = client.get_item(TableName=os.getenv('ROLE_MAP_TABLENAME', 'role_perms'),
                              Key={'auth_token': {'S': lookup_token}})
        if row is not None:
            return row['Item']['role_arn']['S']
        else:
            return None
    else:
        return None


def get_credentials(auth_token):

    arn = None
    if auth_token is not None:
        arn = get_arn(auth_token)

    if arn is not None:
        sts_client = boto3.client('sts')
        credentials = sts_client.assume_role(RoleArn=arn,
                                             DurationSeconds=os.getenv('DEFAULT_DURATION', 900),
                                             RoleSessionName=auth_token)

        ecs_payload = {
            'AccessKeyId': credentials['Credentials']['AccessKeyId'],
            'SecretAccessKey': credentials['Credentials']['SecretAccessKey'],
            'Token': credentials['Credentials']['SessionToken'],
            'Expiration': credentials['Credentials']['Expiration'].isoformat()
        }

        return ecs_payload
    else:
        return None


def handler(event, context):

    logger.debug(event)

    to_return = {
        'headers': {'Content-Type': 'application/json'}
    }

    try:
        if event and 'Authorization' in event['headers']:
            auth_token = event['headers']['Authorization']

            credentials = get_credentials(auth_token)

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


if __name__ == "__main__":
    print(handler({'headers': {'Authorization': os.getenv('AUTH_TOKEN')}}, None))