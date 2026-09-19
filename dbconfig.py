import boto3
from botocore.config import Config

region_name: str = "eu-north-1"

def get_dynamodb_resource() -> boto3.resource:
    """
    Returns a cached boto3 DynamoDB resource with predefined timeouts and adaptive retries.
    """
    config = Config(
        region_name= region_name,
        signature_version='v4',
        retries={
            'max_attempts': 3,
            'mode': 'adaptive'
        },
        connect_timeout=3,
        read_timeout=5
    )

    return boto3.resource('dynamodb', config=config)

def get_dynamodb_client():
    return boto3.client(
        'dynamodb',
        region_name='eu-north-1'
    )