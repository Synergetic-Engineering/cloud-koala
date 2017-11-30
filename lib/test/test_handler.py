# XXX this needs to happen before importing other stuff to set
# env variables
from lib.test import util

import boto3
boto3.setup_default_session(aws_access_key_id='123', aws_secret_access_key='123', region_name='ap-southeast-2')

import base64

import lib.handler


def test_build_response():
    resp = lib.handler.build_response({'test_key': 'test_value'}, 1)
    assert resp['body'] == '{"test_key": "test_value"}'
    assert resp['statusCode'] == 1


def test_success():
    resp = lib.handler.success({'test_key': 'test_value'})
    assert resp['body'] == '{"test_key": "test_value"}'
    assert resp['statusCode'] == 200


def test_get_file_from_event():
    file_name, file_string = lib.handler.get_file_from_event({
        'body': {
            'file_name': 'abc.xlsx',
            'file_string': base64.b64encode('123457'),
        },
    })
    assert file_name == 'abc.xlsx'
    assert file_string == '123457'


@util.setup_mock_resources
def test_get_models():
    resp = lib.handler.get_models(None, None)
    assert resp['statusCode'] == 200
    print resp


@util.setup_mock_resources
def test_add_model():
    with open('lib/test/test.xlsx') as f:
        resp = lib.handler.add_model({
            'body': {
                'file_name': 'abc.xlsx',
                'file_string': base64.b64encode(f.read()),
            },
            }, None)
    assert resp['statusCode'] == 200


@util.setup_mock_resources
def test_get_model():
    resp = lib.handler.get_model({
        'pathParameters': {'model_id': '123abc'},
        }, None)
    assert resp['statusCode'] == 200


@util.setup_mock_resources
def test_update_model():
    with open('lib/test/test.xlsx') as f:
        resp = lib.handler.update_model({
            'pathParameters': {'model_id': '123abc'},
            'body': {
                'file_name': 'abc.xlsx',
                'file_string': base64.b64encode(f.read()),
            },
            }, None)
    assert resp['statusCode'] == 200


@util.setup_mock_resources
def test_delete_model():
    resp = lib.handler.delete_model({
        'pathParameters': {'model_id': '123abc'},
        }, None)
    assert resp['statusCode'] == 200


@util.setup_mock_resources
def test_run_model():

    resp = lib.handler.run_model({
        'pathParameters': {'model_id': '123abc'}, 'body': {},
        }, None)
    assert resp['statusCode'] == 200


@util.setup_mock_resources
def test_compile_model():
    resp = lib.handler.compile_model({
        'Records': [{
            'eventName': 'ObjectCreated:Put',
            's3': {'object': {'key': 'excel_uploads/123abc'}},
            }],
        }, None)
    print resp
