# XXX this needs to happen before importing other stuff to set
# env variables
import test.util

import boto3
from moto import mock_dynamodb2, mock_s3
boto3.setup_default_session(aws_access_key_id='123', aws_secret_access_key='123', region_name='ap-southeast-2')

import handler


def test_build_response():
    resp = handler.build_response({'test_key': 'test_value'}, 1)
    assert resp['body'] == '{"test_key": "test_value"}'
    assert resp['statusCode'] == 1


def test_success():
    resp = handler.success({'test_key': 'test_value'})
    assert resp['body'] == '{"test_key": "test_value"}'
    assert resp['statusCode'] == 200


def test_get_file_from_event():
    file_name, file_string = handler.get_file_from_event({
        'body': {
            'file_name': 'abc.xlsx',
            'file_string': '123457',
        },
    })
    assert file_name == 'abc.xlsx'
    assert file_string == '123457'


@mock_dynamodb2
def test_get_models():
    test.util.create_dynamodb_table()
    resp = handler.get_models(None, None)
    assert resp['statusCode'] == 200
    print resp


@mock_dynamodb2
@mock_s3
def test_add_model():
    test.util.create_dynamodb_table()
    test.util.create_s3_bucket()
    resp = handler.add_model({
        'body': {
            'file_name': 'abc.xlsx',
            'file_string': '123457',
        },
        }, None)
    assert resp['statusCode'] == 200


@mock_dynamodb2
@mock_s3
def test_get_model():
    test.util.create_dynamodb_table()
    test.util.create_s3_bucket()
    resp = handler.get_model({
        'pathParameters': {'model_id': '123abc'},
        }, None)
    assert resp['statusCode'] == 200


@mock_dynamodb2
@mock_s3
def test_update_model():
    test.util.create_dynamodb_table()
    test.util.create_s3_bucket()
    resp = handler.update_model({
        'pathParameters': {'model_id': '123abc'},
        'body': {
            'file_name': 'abc.xlsx',
            'file_string': '123457',
        },
        }, None)
    assert resp['statusCode'] == 200


@mock_dynamodb2
@mock_s3
def test_delete_model():
    test.util.create_dynamodb_table()
    test.util.create_s3_bucket()
    resp = handler.delete_model({
        'pathParameters': {'model_id': '123abc'},
        }, None)
    assert resp['statusCode'] == 200


@mock_dynamodb2
@mock_s3
def test_run_model():
    test.util.create_dynamodb_table()
    test.util.create_s3_bucket()
    resp = handler.run_model({
        'pathParameters': {'model_id': '123abc'}, 'body': {},
        }, None)
    assert resp['statusCode'] == 200
