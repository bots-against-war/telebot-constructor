import datetime
from typing import cast

import tenacity
from telebot import api as tg_api
from tenacity import RetryCallState
from tenacity.retry import (
    retry_all,
    retry_if_exception_message,
    retry_if_exception_type,
)
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_chain, wait_exponential


class wait_from_too_many_requests_error(tenacity.wait.wait_base):
    def __call__(self, retry_state: RetryCallState) -> float:
        if retry_state.outcome is None:
            return 0.0
        if not retry_state.outcome.failed:
            return 0.0
        exc = cast(Exception, retry_state.outcome.exception())
        if not isinstance(exc, tg_api.ApiHTTPException):
            return 0.0
        if exc.error_parameters is None or exc.error_parameters.retry_after is None:
            return 0.0
        return exc.error_parameters.retry_after


def rate_limit_retry():
    return tenacity.AsyncRetrying(
        retry=retry_all(
            retry_if_exception_type(tg_api.ApiHTTPException),
            retry_if_exception_message(match="Too Many Requests"),
        ),
        wait=wait_chain(
            wait_from_too_many_requests_error(),
            wait_exponential(
                multiplier=1,
                max=datetime.timedelta(minutes=3),
                min=datetime.timedelta(seconds=1),
            ),
        ),
        stop=stop_after_attempt(5),
        reraise=True,
    )
