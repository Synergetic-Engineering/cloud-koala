import os
import uuid

import boto3

from openpyxl import load_workbook

from koala.ExcelCompiler import ExcelCompiler
from koala.Spreadsheet import Spreadsheet
from koala.ExcelError import ExcelError


# XXX is having these up at the module level like this best practice?
# - also worth considering how we will mock them for testing
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
s3 = boto3.resource('s3')
bucket = s3.Bucket(os.environ['S3_BUCKET'])


def list_models():
    """
    List the available models in S3
    """
    result = table.scan()
    return {'models': result['Items']}


def add_or_update_model(file_name, file_string, model_id=None):
    """
    Serialise the xlsx_file and upload to S3, return the ID
    """
    model_id = model_id or uuid.uuid4().hex
    bucket.put_object(Key='excel_uploads/{}'.format(model_id), Body=file_string)
    table.put_item(Item={
        'model_id': model_id,
        'file_name': file_name,
    })
    return model_id


def get_model(model_id):
    """
    Get information about the serialised model and Excel file
    e.g. inputs, outputs
    maybe allow for optional level of detail to this?
    """
    result = table.get_item(
        Key={
            'model_id': model_id,
        }
    )
    return result['Item']


def delete_model(model_id):
    """
    Delete the model record from S3 and either archive or delete related files in S3
    """
    table.delete_item(
        Key={
            'model_id': model_id,
        }
    )
    # Archive Objects
    try:
        bucket.put_object(
            Body=bucket.Object('excel_uploads/{}'.format(model_id)).get()['Body'].read(),
            Key='excel_uploads_archive/{}'.format(model_id),
        )
    except:
        pass
    try:
        bucket.put_object(
            Body=bucket.Object('compiled_models/{}'.format(model_id)).get()['Body'].read(),
            Key='compiled_models_archive/{}'.format(model_id),
        )
    except:
        pass
    # Delete Objects
    bucket.delete_objects(Delete={
        'Objects': [
            {'Key': 'excel_uploads/{}'.format(model_id)},
            {'Key': 'compiled_models/{}'.format(model_id)},
        ]
    })

    # TODO Check for error
    return model_id


def run_model(model_id, payload):
    """
    Load the model, set the inputs and return the calculated outputs
    TODO get this working roughly following these steps
      - Get serialised model from S3
      - Load model with koala
      - Extract inputs from payload
      - Set the inputs in the model
      - Extract required outputs from payload (all outputs if none specifically requested)
      - Get the required outputs from the model
      - Build and return response
    """
    compliled_string = bucket.Object('compiled_models/{}'.format(model_id)).get()['Body'].read()
    # XXX HACK Workaround needed for koala spreadsheet loading API
    # - need to write the file to a temp location for koala to read it...
    # - FIX = koala.Spreadsheet / koala.serialize should be updated to take the file contents in directly
    if not os.path.exists('/tmp'):
        os.mkdir('/tmp')
    dummy_file_name = '/tmp/temp_{}.gzip'.format(model_id)
    with open(dummy_file_name, 'wb') as fp:
        fp.write(compliled_string)
    sp = Spreadsheet.load(dummy_file_name)
    # TODO actually run the model and build the results
    results = {}
    # Cleanup previous workaround
    os.remove(dummy_file_name)
    if not os.listdir('/tmp'):
        os.rmdir('/tmp')
    return results


def compile_model(model_id):
    compliled_string = bucket.Object('excel_uploads/{}'.format(model_id)).get()['Body'].read()
    # XXX HACK Workaround needed for koala spreadsheet loading API
    # - need to write the file to a temp location for koala to read it...
    # - then need to write koala compiled file from a temp location...
    # - FIX = koala.Spreadsheet / koala.serialize should be updated to take the file contents in directly
    if not os.path.exists('/tmp'): # mainly required for dev / test environment
        os.mkdir('/tmp')
    dummy_excel_file_name = '/tmp/temp_excel_file_{}.xlsx'.format(model_id)
    with open(dummy_excel_file_name, 'wb') as fp:
        fp.write(compliled_string)
    compiler = ExcelCompiler(dummy_excel_file_name)
    sp = compiler.gen_graph()
    dummy_compiled_file_name = '/tmp/temp_compiled_file_{}.gzip'.format(model_id)
    sp.dump(dummy_compiled_file_name)
    with open(dummy_compiled_file_name, 'r') as fp:
        compiled_file_string = fp.read()
    # Write compiled file to S3 and update dynamodb record
    bucket.put_object(Key='compiled_models/{}'.format(model_id), Body=compiled_file_string)
    table.put_item(Item={
        'model_id': model_id,
        'compiled': True,
    })
    # Cleanup previous workaround
    os.remove(dummy_excel_file_name)
    os.remove(dummy_compiled_file_name)
    if not os.listdir('/tmp'):
        os.rmdir('/tmp')
    return 'model {} compiled successfully'.format(model_id)
