import handler


def test_build_response():
    resp = handler.build_response({'test_key': 'test_value'}, 1)
    assert resp['body'] == '{"test_key": "test_value"}'
    assert resp['statusCode'] == 1


def test_success():
    resp = handler.success({'test_key': 'test_value'})
    assert resp['body'] == '{"test_key": "test_value"}'
    assert resp['statusCode'] == 200


def test_get_xlsx_file_from_event():
    xlsx_file = handler.get_xlsx_file_from_event({})


def test_get_models():
    resp = handler.get_models(None, None)
    assert resp['statusCode'] == 200


def test_add_model():
    resp = handler.add_model({'body': {}}, None)
    assert resp['statusCode'] == 200


def test_get_model():
    resp = handler.add_model({'pathParameters': {'model_id': '123abc'}}, None)
    assert resp['statusCode'] == 200


def test_update_model():
    resp = handler.update_model({'pathParameters': {'model_id': '123abc'}, 'body': {}}, None)
    assert resp['statusCode'] == 200


def test_delete_model():
    resp = handler.delete_model({'pathParameters': {'model_id': '123abc'}}, None)
    assert resp['statusCode'] == 200


def test_run_model():
    resp = handler.run_model({'pathParameters': {'model_id': '123abc'}, 'body': {}}, None)
    assert resp['statusCode'] == 200
