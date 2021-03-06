import base64

try:
    import unzip_requirements
except ImportError:
    print 'WARNING: unzip_requirements failed to import'

import simplejson as json

from lib import model, config


def build_response(body, status, content_type='application/json', filename=None):
    response = {
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
            'Content-Type': content_type,
        },
        'statusCode': status,
    }
    if content_type == 'application/json':
        body = json.dumps(body)
    response['body'] = body
    if filename is not None:
        response['headers']['Content-Disposition'] = 'attachment; filename="%s"' % filename
        response['isBase64Encoded'] = True
    return response


def success(body, content_type='application/json', filename=None):
    response = build_response(body, 200, content_type=content_type, filename=filename)
    return response


def _get_file_from_event(event):
    payload = json.loads(event.get('body') or '{}')
    file_name = payload.get('file_name', '')
    file_string = base64.b64decode(payload.get('file_string', ''))
    config_sheet_name = payload.get('config_sheet_name')
    return file_name, file_string, config_sheet_name


# ===========
# /models API
# ===========

def get_models(event, context):
    """
    Get the available Excel models
    Trigger event: GET https://.../models
    Inputs: None
    Returns: response with a list of available models
    """
    return success(model.list_models())


def add_model(event, context):
    """
    Upload a new Excel model for koala object compilation and serialisation
    Trigger event: POST https://.../models
    Inputs:
      - body: Excel file (required)
    Returns: ID of the created model
    """
    file_name, file_string, config_sheet_name = _get_file_from_event(event)
    return success(model.add_or_update_model(
        file_name,
        file_string,
        config_sheet_name=config_sheet_name,
        ))


def get_model(event, context):
    """
    Get information about a particular model
    Trigger event: GET https://.../models/{model_id}
    Inputs:
      - path parameter: `model_id` (required)
    Returns: An information dictionary about the requested model
    """
    model_id = event['pathParameters']['model_id']
    return success(model.get_model(model_id))


def update_model(event, context):
    """
    Update an existing model
    Trigger event: PUT https://.../models/{model_id}
    Inputs:
      - event.pathParameter: `model_id` (required)
      - event.body: Excel file name (required)
      - event.body: Excel file string (required)
    Returns: ID of the updated model
    """
    model_id = event['pathParameters']['model_id']
    file_name, file_string, config_sheet_name = _get_file_from_event(event)
    res = model.add_or_update_model(
        file_name, file_string, model_id=model_id, config_sheet_name=config_sheet_name)
    return success(res)


def delete_model(event, context):
    """
    Delete an existing model
    Trigger event: DELETE https://.../models/{model_id}
    Inputs:
      - event.pathParameter: `model_id` (required)
    Returns: ID of the deleted model
    """
    model_id = event['pathParameters']['model_id']
    return success(model.delete_model(model_id))


def run_model(event, context):
    """
    Set model inputs and run it to calculate outputs
    Trigger event: POST https://.../models/{model_id}
    Inputs:
      - event.pathParameter: `model_id` (required)
      - event.body: `input_data` (optional)
      - event.body: `outputs` (optional)
    Returns: Outputs of the model
    """
    model_id = event['pathParameters']['model_id']
    try:
        payload = json.loads(event.get('body') or '{}')
    except ValueError as err:
        return build_response("Malformed JSON in request: %s" % err.message, status=422)
    input_dict = payload.get('input_dict', {})
    output_names = payload.get('output_names', [])
    return success(model.run_model(model_id, input_dict, output_names))


def compile_model(event, context):
    """
    Compile a Koala Spreadsheet object from an uploaded Excel file, serialise it and store it in S3
    Trigger event: Object created or modified to `excel_uploads/` in the S3 bucket
    Inputs:
      - `model_id` (required)
    Returns: Status of compilation
    """
    # TODO check how many records there might be (always only 1 or will it collect them?)
    responses = []
    for record in event['Records']:
        if record['eventName'] == 'ObjectCreated:Put':
            model_id = record['s3']['object']['key'].replace('excel_uploads/', '')
            resp = model.compile_model(model_id)
            responses.append(resp)
    return responses


# ===========
# /config API
# ===========

def create_config_sheet(event, context):
    """
    Create a config sheet for a given file
    Trigger event: POST https://.../config
    Inputs:
      - body: Excel file (required)
    Returns: Excel file with the new config sheet
    """
    _, file_string, config_sheet_name = _get_file_from_event(event)
    output_file_string = base64.b64encode(
        config.create_config_sheet(file_string, config_sheet_name=config_sheet_name))
    return success({'file_string': output_file_string})
