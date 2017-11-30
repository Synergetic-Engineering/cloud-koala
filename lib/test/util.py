import os

import boto3
from moto import mock_dynamodb2, mock_s3


os.environ['DYNAMODB_TABLE'] = 'moto-test-table'
os.environ['S3_BUCKET'] = 'moto-test-bucket'


def setup_mock_resources(func):
    def _func(*args, **kwargs):
        create_dynamodb_table()
        create_s3_bucket()
        return func(*args, **kwargs)
    return mock_dynamodb2(mock_s3(_func))


def create_dynamodb_table():
    dynamodb_client = boto3.client("dynamodb")
    try:
        dynamodb_client.create_table(
            TableName=os.environ['DYNAMODB_TABLE'],
            KeySchema=[
                {
                    'AttributeName': 'model_id',
                    'KeyType': 'HASH'
                },
            ],
            AttributeDefinitions=[
                {
                    "AttributeName": "model_id",
                    "AttributeType": "S"
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
    except dynamodb_client.exceptions.ResourceInUseException:
        pass
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    table.put_item(Item={
        'model_id': '123abc',
        'file_name': 'file_name.xlsx',
        'version': '1',
        'compilation_status':'Compiled'
    })
    table.put_item(Item={
        'model_id': '456def',
        'file_name': 'file_name.xlsx',
        'version': '1',
        'compilation_status':'Waiting'
    })


def create_s3_bucket():
    s3_client = boto3.client("s3")
    try:
        s3_client.create_bucket(Bucket=os.environ['S3_BUCKET'])
    except s3_client.exceptions.ResourceInUseException:
        pass
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(os.environ['S3_BUCKET'])
    with open('lib/test/test.xlsx', 'rb') as f:
        file_string = f.read()
        bucket.put_object(
            Bucket=os.environ['S3_BUCKET'],
            Key='excel_uploads/123abc',
            Body=file_string,
        )
        bucket.put_object(
            Bucket=os.environ['S3_BUCKET'],
            Key='excel_uploads/456def',
            Body=file_string,
        )
    with open('lib/test/test.gzip', 'rb') as f:
        bucket.put_object(
            Bucket=os.environ['S3_BUCKET'],
            Key='compiled_models/123abc',
            Body=f.read(),
        )
