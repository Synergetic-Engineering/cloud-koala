import base64

# XXX this needs to happen before importing other stuff to set
# env variables
from lib.tests import util

import boto3
boto3.setup_default_session(aws_access_key_id='123', aws_secret_access_key='123', region_name='ap-southeast-2')

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
    file_name, file_string, config_sheet_name = lib.handler._get_file_from_event({
        'body': '{"file_name": "abc.xlsx", "file_string": "%s", "config_sheet_name": "configsheet"}' % base64.b64encode('blinky-bill'),
    })
    assert file_name == 'abc.xlsx'
    assert file_string == 'blinky-bill'
    assert config_sheet_name == 'configsheet'


@util.setup_mock_resources
def test_get_models():
    resp = lib.handler.get_models(None, None)
    assert resp['statusCode'] == 200
    print resp


@util.setup_mock_resources
def test_add_model():
    with open('lib/tests/test.xlsx') as f:
        resp = lib.handler.add_model({
            'body': '{"file_name": "abc.xlsx", "file_string": "%s"}' % base64.b64encode(f.read()),
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
    with open('lib/tests/test.xlsx') as f:
        resp = lib.handler.update_model({
            'pathParameters': {'model_id': '123abc'},
            'body': '{"file_name": "abc.xlsx", "file_string": "%s"}' % base64.b64encode(f.read()),
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
        'pathParameters': {'model_id': '123abc'},
        'body': '{"input_dict": {"Sheet1!B2": 2}, "output_names": ["Sheet1!B12"]}',
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


@util.setup_mock_resources
def test_create_config_sheet():
    # TODO make more meaningful to functionality of model_config
    with open('lib/tests/test.xlsx', 'rb') as f:
        resp = lib.handler.create_config_sheet({
            'body': '{"file_name": "abc.xlsx", "file_string": "%s"}' % base64.b64encode(f.read()),
            }, None)
    assert resp['statusCode'] == 200
