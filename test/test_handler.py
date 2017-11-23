import handler


def test_build_response():
    resp = handler.build_response({'test_key': 'test_value'}, 1)
    assert resp['body'] == '{"test_key": "test_value"}'
    assert resp['statusCode'] == 1


def test_success():
    resp = handler.success({'test_key': 'test_value'})
    assert resp['body'] == '{"test_key": "test_value"}'
    assert resp['statusCode'] == 200
