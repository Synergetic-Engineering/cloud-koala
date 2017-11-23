import lib


def test_list_models():
    lib.list_models()


def test_add_or_update_model():
    lib.add_or_update_model('')
    lib.add_or_update_model('', model_id='123abc')


def test_get_model():
    lib.get_model('123abc')


def test_delete_model():
    lib.delete_model('123abc')


def test_run_model():
    lib.run_model('123abc', {})
