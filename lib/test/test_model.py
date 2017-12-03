import os

# XXX this needs to happen before importing other stuff to set
# env variables
from lib.test import util

import boto3
boto3.setup_default_session(aws_access_key_id='123', aws_secret_access_key='123', region_name='ap-southeast-2')

import lib.model


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
s3 = boto3.resource('s3')
bucket = s3.Bucket(os.environ['S3_BUCKET'])

def _get_table_model_ids():
    return [each['model_id'] for each in table.scan()['Items']]

def _get_bucket_model_ids():
    return [each.key for each in bucket.objects.all()]

def _get_table_model_parameter(model_id, parameter):
    for each in table.scan()['Items']:
        if each['model_id'] == model_id:
            return each[parameter]

def _get_file_string():
    with open('lib/test/test.xlsx', 'r') as f:
        return f.read()


@util.setup_mock_resources
def test_list_models():
    lib.model.list_models()


@util.setup_mock_resources
def test_add_model():
    file_string = _get_file_string()
    model_id = lib.model.add_or_update_model('file_name', file_string)
    # check model_id is in dynamodb and s3
    assert model_id in _get_table_model_ids()
    assert 'excel_uploads/{}'.format(model_id) in _get_bucket_model_ids()


@util.setup_mock_resources
def test_update_model():
    file_string = _get_file_string()
    lib.model.add_or_update_model('file_name', file_string, model_id='123abc')
    # check model_id is still in dynamodb and s3
    assert '123abc' in _get_table_model_ids()
    assert 'excel_uploads/123abc' in _get_bucket_model_ids()
    # check version==2
    assert _get_table_model_parameter('123abc', 'version') == str(2)


@util.setup_mock_resources
def test_get_model():
    lib.model.get_model('123abc')


@util.setup_mock_resources
def test_delete_model():
    print lib.model.delete_model('123abc')
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


@util.setup_mock_resources
def test_run_model():
    # Multiple inputs and outputs
    result = lib.model.run_model('123abc', {'Sheet1!B2': 2, 'Sheet1!B3': 3}, ['Sheet1!B11','Sheet1!B12'])
    assert result == {'Sheet1!B11': 10.0,'Sheet1!B12': 5.7}
    # No inputs or outputs
    result = lib.model.run_model('123abc', {}, [])
    assert result == {}
    # No inputs and output specified
    result = lib.model.run_model('123abc', {}, ['Sheet1!B12'])
    assert result == {'Sheet1!B12': 5.5}
    # Inputs specified and no outputs
    result = lib.model.run_model('123abc', {'Sheet1!B2': 2}, [])
    assert result == {}
    # Multiple inputs and no outputs
    result = lib.model.run_model('123abc', {'Sheet1!B2': 2, 'Sheet1!B4': 3, 'Sheet1!B6': 7}, [])
    assert result == {}
    # Multiple outputs and no inputs
    result = lib.model.run_model('123abc', {}, ['Sheet1!B11','Sheet1!B12'])
    assert result == {'Sheet1!B11': 10.0,'Sheet1!B12': 5.5}


@util.setup_mock_resources
def test_compile_model():
    lib.model.compile_model('456def')
    # check in s3 compiled models bucket
    assert 'compiled_models/456def' in _get_bucket_model_ids()


@util.setup_mock_resources
def test_get_model_config():
    # TODO make more meaningful to functionality of get_model_config
    file_string = _get_file_string()
    assert lib.model.get_model_config(file_string) == file_string
