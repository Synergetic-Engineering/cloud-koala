import os
import time
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

def _update_bucket_parameter(model_id, param_name, content):
    table.update_item(
        Key={'model_id': model_id},
        UpdateExpression='SET #name = :value',
        ExpressionAttributeNames={"#name":param_name},
        ExpressionAttributeValues={":value":content}
    )


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
    key = {'model_id': model_id or uuid.uuid4().hex}
    if model_id is not None:
        item_record = table.get_item(Key=key).get('Item', {})
    if model_id is None or not item_record:
        item_record = {
            'model_id': key['model_id'],
            'created_at': str(int(time.time())),
            'version': str(0),
            'compilation_status':'Waiting',
        }
    item_record['file_name'] = file_name
    item_record['version'] = str(int(item_record['version'])+1)
    item_record['updated_at'] = str(int(time.time()))
    table.put_item(Item=item_record)
    bucket.put_object(Key='excel_uploads/{}'.format(item_record['model_id']), Body=file_string)
    return key['model_id']


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
    # see if compiled model compiled
    comp_stat=""
    for each in table.scan()['Items']:
        if each['model_id']==model_id:
            comp_stat = each['compilation_status']
    if comp_stat!="Compiled":
        return 'Model Not Compiled'
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
    _update_bucket_parameter(model_id, "compilation_status", "Compiling")
    # XXX HACK Workaround needed for koala spreadsheet loading API
    # - need to write the file to a temp location for koala to read it...
    # - then need to write koala compiled file from a temp location...
    # - FIX = koala.Spreadsheet / koala.serialize should be updated to take the file contents in directly
    if not os.path.exists('/tmp'): # mainly required for dev / test environment
        os.mkdir('/tmp')
    dummy_excel_file_name = '/tmp/temp_excel_file_{}.xlsx'.format(model_id)
    with open(dummy_excel_file_name, 'wb') as fp:
        fp.write(compliled_string)
    try:
        compiler = ExcelCompiler(dummy_excel_file_name)
        sp = compiler.gen_graph()
    except IOError as er:
        print er
        _update_bucket_parameter(model_id, "compilation_status", "Failed (Invalid Excel File)")
        return_str = 'model {} did not compile'.format(model_id)
    except Exception as er:
        if str(er)=='File is not a zip file':
            _update_bucket_parameter(model_id, "compilation_status", "Failed (Invalid File Type)")
            print er
        else:
            _update_bucket_parameter(model_id, "compilation_status", "Failed (Generic Error)")
            print er
        return_str = 'model {} did not compile'.format(model_id)
    else:
        dummy_compiled_file_name = '/tmp/temp_compiled_file_{}.gzip'.format(model_id)
        sp.dump(dummy_compiled_file_name)
        with open(dummy_compiled_file_name, 'r') as fp:
            compiled_file_string = fp.read()
        # Write compiled file to S3 and update dynamodb record
        bucket.put_object(Key='compiled_models/{}'.format(model_id), Body=compiled_file_string)
        _update_bucket_parameter(model_id, "compilation_status", "Compiled")
        # Cleanup previous workaround
        os.remove(dummy_compiled_file_name)
        return_str = 'model {} compiled'.format(model_id)
    finally:
        # Cleanup previous workaround
        os.remove(dummy_excel_file_name)
        if not os.listdir('/tmp'):
            os.rmdir('/tmp')
        return return_str
