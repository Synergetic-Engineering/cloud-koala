# XXX this needs to happen before importing other stuff to set
# env variables
import test.util

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


def test_get_models():
    resp = handler.get_models(None, None)
    assert resp['statusCode'] == 200


def test_add_model():
    resp = handler.add_model({
        'body': {
            'file_name': 'abc.xlsx',
            'file_string': '123457',
        },
        }, None)
    assert resp['statusCode'] == 200


def test_get_model():
    resp = handler.add_model({
        'pathParameters': {'model_id': '123abc'},
        }, None)
    assert resp['statusCode'] == 200


def test_update_model():
    resp = handler.update_model({
        'pathParameters': {'model_id': '123abc'},
        'body': {
            'file_name': 'abc.xlsx',
            'file_string': '123457',
        },
        }, None)
    assert resp['statusCode'] == 200


def test_delete_model():
    resp = handler.delete_model({
        'pathParameters': {'model_id': '123abc'},
        }, None)
    assert resp['statusCode'] == 200


def test_run_model():
    resp = handler.run_model({
        'pathParameters': {'model_id': '123abc'}, 'body': {},
        }, None)
    assert resp['statusCode'] == 200
