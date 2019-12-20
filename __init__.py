import boto3
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

if os.getenv('AWS_REGION'):
    boto3.setup_default_session(region_name=os.getenv('AWS_REGION'))
