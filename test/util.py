import os

import boto3

from koala.ExcelCompiler import ExcelCompiler

# XXX need to set these environment variables before importing handler/lib
# Figure there'll be a better way to do this once we use moto?
# XXX - shouldn't actually be deployed resources, the should be mock ones using moto
os.environ['DYNAMODB_TABLE'] = 'moto-test-table'
os.environ['S3_BUCKET'] = 'moto-test-bucket'

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
    with open('test/test.xlsx', 'r') as f:
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
    with open('test/test.gzip', 'r') as f:
        bucket.put_object(
            Bucket=os.environ['S3_BUCKET'],
            Key='compiled_models/123abc',
            Body=f.read(),
        )
