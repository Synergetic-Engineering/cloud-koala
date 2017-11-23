import json

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


def get_xlsx_file_from_event(event):
    # TODO work out how we want to expect the xlsx file to be included
    # Should this serialize it?
    return ''


# GET https://.../models
def get_models(event, context):
    return success(lib.list_models())


# POST https://.../models
def add_model(event, context):
    xlsx_file = get_xlsx_file_from_event(event)
    return success(lib.add_or_update_model(xlsx_file))


# GET https://.../models/{model_id}
def get_model(event, context):
    model_id = event['pathParameters']['model_id']
    return success(lib.get_model(model_id))


# PUT https://.../models/{model_id}
def update_model(event, context):
    model_id = event['pathParameters']['model_id']
    xlsx_file = get_xlsx_file_from_event(event)
    return success(lib.add_or_update_model(xlsx_file, model_id=model_id))


# DELETE https://.../models/{model_id}
def delete_model(event, context):
    model_id = event['pathParameters']['model_id']
    return success(lib.delete_model(model_id))


# POST https://.../models/{model_id}
def run_model(event, context):
    model_id = event['pathParameters']['model_id']
    try:
        payload = json.loads(event.get('body') or '{}')
    except ValueError as err:
        return build_response("Malformed JSON in request: %s" % err.message, status=422)
    return success(lib.run_model(model_id, payload))
