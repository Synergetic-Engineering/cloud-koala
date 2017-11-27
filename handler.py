import json

try:
    import unzip_requirements
except ImportError:
    pass

import lib


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


def get_file_from_event(event):
    # TODO double check how we want to expect the xlsx file to be included
    file_name = event['body']['file_name']
    file_string = event['body']['file_string']
    return file_name, file_string


def get_models(event, context):
    """
    Get the available Excel models
    Trigger event: GET https://.../models
    Inputs: None
    Returns: response with a list of available models
    """
    return success(lib.list_models())


def add_model(event, context):
    """
    Upload a new Excel model for koala object compilation and serialisation
    Trigger event: POST https://.../models
    Inputs:
      - body: Excel file (required)
    Returns: ID of the created model
    """
    file_name, file_string = get_file_from_event(event)
    return success(lib.add_or_update_model(file_name, file_string))


def get_model(event, context):
    """
    Get information about a particular model
    Trigger event: GET https://.../models/{model_id}
    Inputs:
      - path parameter: `model_id` (required)
    Returns: An information dictionary about the requested model
    """
    model_id = event['pathParameters']['model_id']
    return success(lib.get_model(model_id))


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
    file_name, file_string = get_file_from_event(event)
    return success(lib.add_or_update_model(file_name, file_string, model_id=model_id))


def delete_model(event, context):
    """
    Delete an existing model
    Trigger event: DELETE https://.../models/{model_id}
    Inputs:
      - event.pathParameter: `model_id` (required)
    Returns: ID of the deleted model
    """
    model_id = event['pathParameters']['model_id']
    return success(lib.delete_model(model_id))


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
    return success(lib.run_model(model_id, payload))


def compile_model(event, context):
    """
    Compile a Koala Spreadsheet object from an uploaded Excel file, serialise it and store it in S3
    Trigger event: Object created or modified to `excel_uploads/` in the S3 bucket
    Inputs:
      - `model_id` (required)
    Returns: Status of compilation
    """
    # TODO check how many records there might be (always only 1 or will it collect them?)
    for record in event['Records']:
        if record['eventName'] == 'ObjectCreated:Put':
            model_id = record['s3']['object']['key'].replace('excel_uploads/', '')
            lib.compile_model(model_id)
