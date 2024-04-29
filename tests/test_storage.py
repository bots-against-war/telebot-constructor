import pytest

from telebot_constructor.store.form_results import GlobalFormId


@pytest.mark.parametrize(
    "global_form_id",
    [
        GlobalFormId("user", "bot", "form"),
        GlobalFormId("user", "bot", "form/with/slashes"),
        GlobalFormId("user", "", "form"),
        GlobalFormId("", "", "form"),
        GlobalFormId("*", "bot", "form"),
        GlobalFormId("*", "*", "form"),
    ],
)
def test_global_form_id_serialization(global_form_id: GlobalFormId):
    key = global_form_id.as_key()
    assert isinstance(key, str)
    assert GlobalFormId.from_key(key) == global_form_id
