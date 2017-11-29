# XXX this needs to happen before importing other stuff to set
# env variables
import test.util

import boto3
from moto import mock_dynamodb2, mock_s3
boto3.setup_default_session(aws_access_key_id='123', aws_secret_access_key='123', region_name='ap-southeast-2')

import lib

import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
s3 = boto3.resource('s3')
bucket = s3.Bucket(os.environ['S3_BUCKET'])

def _get_table_model_ids():
    model_idList = []
    # Or use in lib.list_models()... but assumes lib.list_models() is functional
    for each in table.scan()['Items']:
        model_idList.append(each['model_id'])
    return model_idList

def _get_bucket_model_ids():
    model_idList = []
    for each in bucket.objects.all():
        model_idList.append(each.key)
    return model_idList


@mock_dynamodb2
@mock_s3
def test_list_models():
    test.util.create_dynamodb_table()
    test.util.create_s3_bucket()
    lib.list_models()


@mock_dynamodb2
@mock_s3
def test_add_or_update_model():
    test.util.create_dynamodb_table()
    test.util.create_s3_bucket()
    with open('test/test.xlsx', 'r') as f:
        file_string = f.read()
    lib.add_or_update_model('file_name', file_string)
    lib.add_or_update_model('file_name', file_string, model_id='123abc')


@mock_dynamodb2
@mock_s3
def test_get_model():
    test.util.create_dynamodb_table()
    test.util.create_s3_bucket()
    lib.get_model('123abc')


@mock_dynamodb2
@mock_s3
def test_delete_model():
    test.util.create_dynamodb_table()
    test.util.create_s3_bucket()
    lib.delete_model('123abc')
    # check out of dynamodb table
    assert '123abc' not in _get_table_model_ids()
    # S3 Bucket Checks
    # check out of excel_uploads
    assert 'excel_uploads/123abc' not in _get_bucket_model_ids()
    # check in excel_uploads_archive
    assert 'excel_uploads_archive/123abc' in _get_bucket_model_ids()
    # check out of compiled_models
    assert 'compiled_models/123abc' not in _get_bucket_model_ids()
    # check in excel_uploads_archive
    assert 'compiled_models_archive/123abc' in _get_bucket_model_ids()


@mock_dynamodb2
@mock_s3
def test_run_model():
    test.util.create_dynamodb_table()
    test.util.create_s3_bucket()
    lib.run_model('123abc', {})


@mock_dynamodb2
@mock_s3
def test_compile_model():
    test.util.create_dynamodb_table()
    test.util.create_s3_bucket()
    lib.compile_model('123abc')
    # check in compiled_models
    assert 'compiled_models/123abc' in _get_bucket_model_ids()
