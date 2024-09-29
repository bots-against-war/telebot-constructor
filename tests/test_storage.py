import time

import pytest
from telebot_components.redis_utils.emulation import RedisEmulation

from telebot_constructor.store.form_results import (
    TIMESTAMP_KEY,
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

    form_id = GlobalFormId(username="test", bot_id="testbot", form_block_id="testform")

    now = time.time()

    await form_results_store.save(form_id, result={TIMESTAMP_KEY: now - 100})
    await form_results_store.save(form_id, result={TIMESTAMP_KEY: now - 80})
    await form_results_store.save(form_id, result={TIMESTAMP_KEY: now - 60})
    await form_results_store.save(form_id, result={TIMESTAMP_KEY: now - 40})
    await form_results_store.save(form_id, result={TIMESTAMP_KEY: now - 20})
    await form_results_store.save(form_id, result={TIMESTAMP_KEY: now})

    async def len_matching_filter(filter: FormResultsFilter):
        return len(await form_results_store.load(form_id, filter=filter, load_page_size=load_page_size))

    assert await len_matching_filter(FormResultsFilter(None, None)) == 6
    assert await len_matching_filter(FormResultsFilter(min_timestamp=now - 50, max_timestamp=None)) == 3
    assert await len_matching_filter(FormResultsFilter(min_timestamp=now - 50, max_timestamp=now + 10)) == 3
    assert await len_matching_filter(FormResultsFilter(min_timestamp=now - 70, max_timestamp=now + 10)) == 4
    assert await len_matching_filter(FormResultsFilter(min_timestamp=now - 70, max_timestamp=now - 10)) == 3
    assert await len_matching_filter(FormResultsFilter(min_timestamp=now - 110, max_timestamp=now - 10)) == 5
    assert await len_matching_filter(FormResultsFilter(min_timestamp=now - 110, max_timestamp=None)) == 6
    assert await len_matching_filter(FormResultsFilter(min_timestamp=None, max_timestamp=now - 90)) == 1
