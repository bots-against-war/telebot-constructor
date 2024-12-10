import time

import pytest
from telebot_components.redis_utils.emulation import RedisEmulation

from telebot_constructor.store.form_results import (
    TIMESTAMP_KEY,
    FormResult,
    FormResultsFilter,
    FormResultsStore,
    GlobalFormId,
)


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


@pytest.mark.parametrize(
    "load_page_size",
    [
        pytest.param(1),
        pytest.param(2),
        pytest.param(3),
        pytest.param(5),
        pytest.param(10),
        pytest.param(100),
    ],
)
async def test_form_results_load_with_filter(load_page_size: int):
    redis = RedisEmulation()
    form_results_store = FormResultsStore(redis)

    form_id = GlobalFormId(owner_id="test", bot_id="testbot", form_block_id="testform")

    now = time.time()
    all_results: list[FormResult] = [
        {TIMESTAMP_KEY: now - 100},
        {TIMESTAMP_KEY: now - 80},
        {TIMESTAMP_KEY: now - 60},
        {TIMESTAMP_KEY: now - 40},
        {TIMESTAMP_KEY: now - 20},
        {TIMESTAMP_KEY: now},
    ]

    for r in all_results:
        await form_results_store.save(form_id, result=r)

    async def matching(filter: FormResultsFilter):
        results, is_full = await form_results_store.load(
            form_id,
            filter=filter,
            load_page_size=load_page_size,
            max_results_count=1000,
        )
        assert is_full
        return results

    assert await matching(FormResultsFilter(None, None)) == all_results
    assert await matching(FormResultsFilter(min_timestamp=now - 50, max_timestamp=None)) == all_results[3:]
    assert await matching(FormResultsFilter(min_timestamp=now - 50, max_timestamp=now + 10)) == all_results[3:]
    assert await matching(FormResultsFilter(min_timestamp=now - 70, max_timestamp=now + 10)) == all_results[2:]
    assert await matching(FormResultsFilter(min_timestamp=now - 70, max_timestamp=now - 10)) == all_results[2:5]
    assert await matching(FormResultsFilter(min_timestamp=now - 110, max_timestamp=now - 10)) == all_results[0:5]
    assert await matching(FormResultsFilter(min_timestamp=now - 110, max_timestamp=None)) == all_results[0:6]
    assert await matching(FormResultsFilter(min_timestamp=None, max_timestamp=now - 90)) == all_results[0:1]
