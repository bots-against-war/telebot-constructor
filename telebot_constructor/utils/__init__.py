import collections
import functools
import logging
from typing import (
    Any,
    Awaitable,
    Callable,
    Generator,
    Iterable,
    Optional,
    TypeVar,
    Union,
    cast,
)

import telegramify_markdown  # type: ignore
from telebot import types as tg
from telebot.types.service import HandlerFunction, HandlerResult
from telebot_components.utils import TextMarkup, html_link

from telebot_constructor.utils.pydantic import LocalizableText

logger = logging.getLogger(__name__)


def non_capturing_handler(tg_update_handler: Callable[[Any], Awaitable[Optional[HandlerResult]]]) -> HandlerFunction:
    """
    Decorator ensuring that a handler is non-capturing, i.e. it processes an update and bot
    continues testing other handlers
    """

    @functools.wraps(tg_update_handler)
    async def wrapper(update_content) -> HandlerResult:
        try:
            res = await tg_update_handler(update_content)
            if res is None:
                return HandlerResult(continue_to_other_handlers=True)
            res.continue_to_other_handlers = True
            return res
        except Exception:
            logger.exception(
                f"Error processing update ({update_content}) with handler, continuing to other handlers anyway"
            )
            return HandlerResult(continue_to_other_handlers=True)

    return cast(HandlerFunction, wrapper)


AnyChatId = Union[str, int]


def parse_any_chat_id(s: str) -> AnyChatId:
    try:
        return int(s)
    except ValueError:
        return s


ValueT = TypeVar("ValueT")


def validate_unique(items: Iterable[ValueT], items_name: str, prefix: str = "") -> None:
    item_counter = collections.Counter(items)
    repeating = {v: count for v, count in item_counter.items() if count > 1}
    if repeating:
        raise ValueError(
            prefix
            + f"All {items_name} must be unique, but there are duplicates: "
            + ", ".join(str(v) for v in repeating.keys())
        )


def format_telegram_user(user: tg.User, with_id: bool) -> str:
    full_name = user.full_name
    appendix = []
    if user.username:
        appendix.append("@" + user.username)
    if with_id:
        appendix.append("#" + str(user.id))
    if appendix:
        appendix_str = ", ".join(appendix)
        return f"{full_name} ({appendix_str})"
    else:
        return full_name


def telegram_user_link_raw(user_id: int, title: str) -> str:
    return html_link(href=f"tg://user?id={user_id}", text=title)


def telegram_user_link(user: tg.User) -> str:
    return telegram_user_link_raw(user_id=user.id, title=format_telegram_user(user, with_id=False))


ItemT = TypeVar("ItemT")


def without_nones(it: Iterable[Optional[ItemT]]) -> list[ItemT]:
    return [i for i in it if i is not None]


SizeT = Union[int, float]


def iter_batches(
    seq: Iterable[ItemT],
    size: SizeT,
    *,
    size_func: Callable[[ItemT], SizeT] = lambda _: 1,
) -> Generator[list[ItemT], None, None]:
    """
    Iterate a sequence in batches of specified size. Size can be any additive quantity (i.e.
    batch size is the sum of item sizes). The default is a regular count-based batching.

    Please note that for custom size_func the batch can exceed the target size if it contains larger
    elements. If this is undesirable, filter the iterable in advance.

    Basic use:
    >>> list(iter_batches(['A', 'B', 'C', 'D', 'E'], size=2))
    [['A', 'B'], ['C', 'D'], ['E']]

    With customized size func:
    >>> list(iter_batches(['hello world', 'foo', 'bar', 'foobar', 'baz'], size=8, size_func=len))
    [['hello world'], ['foo', 'bar'], ['foobar'], ['baz']]
    >>> list(iter_batches([1, 2, 3, 6, 1, 1, 1], size=3, size_func=lambda x: x))
    [[1, 2], [3], [6], [1, 1, 1]]
    """
    batch: list[ItemT] = []
    current_size: SizeT = 0
    for item in seq:
        item_size = size_func(item)
        if current_size + item_size > size:
            if batch:
                yield batch
            batch = []
            current_size = 0
        batch.append(item)
        current_size += item_size

    if batch:
        yield batch


def page_params_to_redis_indices(offset: int, count: int) -> tuple[int, int]:
    """
    Convert offset and count pagination params to slice start and end indices.
    Resulting indices follow Redis conventions (negative for counting from the end of the sequence,
    both ends included in the slice). Offset goes from 0 (last page) to positive values for
    earlier entries.
    """
    if offset < 0:
        raise ValueError(f"offset must be non-negative, got {offset=}")
    if count < 0:
        raise ValueError(f"count must be non-negative, got {count=}")
    end = -1 - offset  # offset 0 = last = -1, offset 1 = next-to-last = -2, etc
    start = end - (count - 1)  # redis indices are inclusive, so subtract one from count
    return start, end


def preprocess_markdown_for_telegram(text: str) -> str:
    if not text:
        return text
    return telegramify_markdown.markdownify(text)


def preprocess_for_telegram(text: LocalizableText, markup: TextMarkup) -> LocalizableText:
    if markup is not TextMarkup.MARKDOWN:
        return text
    else:
        # we store texts in a more or less vanilla markdown, but telegram
        # requires some extra processing provided by telegramify_markdown package
        if isinstance(text, str):
            return preprocess_markdown_for_telegram(text)
        else:
            return {lang: preprocess_markdown_for_telegram(translation) for lang, translation in text.items()}
