import os

# lib.util needs to be imported before lib.model and boto3 to set env variables
from lib.tests import util
import lib.model

import boto3


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
s3 = boto3.resource('s3')
bucket = s3.Bucket(os.environ['S3_BUCKET'])


def _get_bucket_model_ids():
    return [each.key for each in bucket.objects.all()]


@util.setup_mock_resources
def test_list_models():
    lib.model.list_models()


@util.setup_mock_resources
def test_add_model():
    file_string = util.get_file_string()
    model_id = lib.model.add_or_update_model('file_name', file_string)
    # check dynamodb record
    dynamodb_record = table.get_item(Key={'model_id': model_id})['Item']
    assert dynamodb_record['file_name'] == 'file_name'
    assert dynamodb_record['compilation_status'] == 'Waiting'
    assert dynamodb_record['config_info'] == {'err': 'Config sheet `cloud-koala-config` not found'}
    assert dynamodb_record['version'] == '1'
    # check model is in s3
    assert 'excel_uploads/{}'.format(model_id) in _get_bucket_model_ids()


@util.setup_mock_resources
def test_add_model_with_existing_config_sheet():
    file_string = util.get_file_string(file_name='lib/tests/test_with_existing_config_sheet.xlsx')
    model_id = lib.model.add_or_update_model(
        'file_name',
        file_string,
        config_sheet_name='config_sheet_test',
        )
    # check dynamodb record
    dynamodb_record = table.get_item(Key={'model_id': model_id})['Item']
    assert dynamodb_record['file_name'] == 'file_name'
    assert dynamodb_record['compilation_status'] == 'Waiting'
    assert isinstance(dynamodb_record['config_info'], list)
    assert len(dynamodb_record['config_info']) == 3
    assert dynamodb_record['version'] == '1'
    # check model is in s3
    assert 'excel_uploads/{}'.format(model_id) in _get_bucket_model_ids()


@util.setup_mock_resources
def test_update_model():
    file_string = util.get_file_string()
    lib.model.add_or_update_model('file_name', file_string, model_id='123abc')
    # check dynamodb record
    dynamodb_record = table.get_item(Key={'model_id': '123abc'})['Item']
    assert dynamodb_record['file_name'] == 'file_name'
    assert dynamodb_record['compilation_status'] == 'Waiting'
    assert dynamodb_record['config_info'] == {'err': 'Config sheet `cloud-koala-config` not found'}
    assert dynamodb_record['version'] == '2'
    # check model is in s3
    assert 'excel_uploads/123abc' in _get_bucket_model_ids()


@util.setup_mock_resources
def test_get_model():
    lib.model.get_model('123abc')


@util.setup_mock_resources
def test_delete_model():
    print lib.model.delete_model('123abc')
    # check out of dynamodb table
    assert 'Item' not in table.get_item(Key={'model_id': '123abc'})
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
    result = lib.model.run_model(
        '123abc',
        {'Sheet1!B2': 2, 'Sheet1!B3': 3}, ['Sheet1!B11', 'Sheet1!B12']
        )
    assert result == {'Sheet1!B11': 10.0, 'Sheet1!B12': 5.7}
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
    result = lib.model.run_model('123abc', {}, ['Sheet1!B11', 'Sheet1!B12'])
    assert result == {'Sheet1!B11': 10.0, 'Sheet1!B12': 5.5}


@util.setup_mock_resources
def test_compile_model():
    lib.model.compile_model('456def')
    # check in s3 compiled models bucket
    assert 'compiled_models/456def' in _get_bucket_model_ids()
