import time

from cryptography.fernet import Fernet
from telebot import types as tg
from telebot.test_util import MethodCall
from telebot.types import Dictionaryable
from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.utils.secrets import RedisSecretStore, SecretStore


def dummy_secret_store(redis: RedisInterface) -> SecretStore:
    return RedisSecretStore(
        redis,
        encryption_key=Fernet.generate_key().decode("utf-8"),
        secrets_per_user=100,
        secret_max_len=1000,
        scope_secrets_to_user=True,
    )


def tg_update_message_to_bot(user_id: int, first_name: str, text: str) -> tg.Update:
    return tg.Update(
        update_id=1,
        message=tg.Message(
            message_id=1,
            from_user=tg.User(id=user_id, is_bot=False, first_name=first_name),
            date=int(time.time()),
            chat=tg.Chat(id=user_id, type="private", first_name=first_name),
            content_type="text",
            options={"text": text},
            json_string="",
        ),
        edited_message=None,
        channel_post=None,
        edited_channel_post=None,
        inline_query=None,
        chosen_inline_result=None,
        callback_query=None,
        shipping_query=None,
        pre_checkout_query=None,
        poll=None,
        poll_answer=None,
        my_chat_member=None,
        chat_member=None,
        chat_join_request=None,
        _json_dict={},
    )


def tg_update_callback_query(user_id: int, first_name: str, callback_query: str) -> tg.Update:
    return tg.Update(
        update_id=1,
        message=None,
        edited_message=None,
        channel_post=None,
        edited_channel_post=None,
        inline_query=None,
        chosen_inline_result=None,
        callback_query=tg.CallbackQuery(
            id=123456,
            from_user=tg.User(id=user_id, is_bot=False, first_name=first_name),
            data=callback_query,
            chat_instance=None,
            json_string=None,
            message=tg.Message(
                message_id=1,
                from_user=tg.User(id=user_id, is_bot=False, first_name=first_name),
                date=int(time.time()),
                chat=tg.Chat(id=user_id, type="private", first_name=first_name),
                content_type="text",
                options={},
                json_string="",
            ),
        ),
        shipping_query=None,
        pre_checkout_query=None,
        poll=None,
        poll_answer=None,
        my_chat_member=None,
        chat_member=None,
        chat_join_request=None,
        _json_dict={},
    )


def assert_dict_includes(actual: dict, included: dict) -> None:
    """Actual dict is allowed to have extra keys beyond those required"""
    for required_key, required_value in included.items():
        assert required_key in actual, f"{actual} misses required key {required_key!r}"
        assert (
            actual[required_key] == required_value
        ), f"{actual} contains {required_key!r}: {actual[required_key]} != {required_value}"


def assert_dicts_include(actual_dicts: list[dict], required_subdicts: list[dict]) -> None:
    assert len(actual_dicts) == len(required_subdicts), (
        f"actual dicts list has mismatching size: {len(actual_dicts)} != {len(required_subdicts)}: "
        + f"{actual_dicts = }, {required_subdicts = }"
    )
    for actual, required in zip(actual_dicts, required_subdicts):
        assert_dict_includes(actual, required)


def assert_method_call_kwargs_include(method_calls: list[MethodCall], required_call_kwargs: list[dict]) -> None:
    call_kwargs = [mc.full_kwargs for mc in method_calls]
    assert_dicts_include(call_kwargs, required_call_kwargs)


def assert_method_call_dictified_kwargs_include(
    method_calls: list[MethodCall], required_call_kwargs: list[dict]
) -> None:
    preprocessed_kwargs = [
        {k: v.to_dict() for k, v in mc.full_kwargs.items() if isinstance(v, Dictionaryable)} for mc in method_calls
    ]
    assert_dicts_include(preprocessed_kwargs, required_call_kwargs)
