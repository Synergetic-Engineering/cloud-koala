# XXX this needs to happen before importing other stuff to set
# env variables
import test.util

import boto3
from moto import mock_dynamodb2, mock_s3
boto3.setup_default_session(aws_access_key_id='123', aws_secret_access_key='123', region_name='ap-southeast-2')

import lib


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
    lib.add_or_update_model('file_name', 'file_string')
    lib.add_or_update_model('file_name', 'file_string', model_id='123abc')


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


@mock_dynamodb2
@mock_s3
def test_run_model():
    test.util.create_dynamodb_table()
    test.util.create_s3_bucket()
    lib.run_model('123abc', {})
