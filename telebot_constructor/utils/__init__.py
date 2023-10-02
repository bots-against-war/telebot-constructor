import logging
from typing import Any, Awaitable, Callable, Optional

from telebot.types.service import HandlerFunction, HandlerResult

logger = logging.getLogger(__name__)


def non_capturing_handler(tg_update_handler: Callable[[Any], Awaitable[Optional[HandlerResult]]]) -> HandlerFunction:
    """
    Decorator ensuring that a handler is non-capturing, i.e. it processes an update and bot
    continues testing other handlers
    """

    async def wrapper(*args, **kwargs) -> HandlerResult:
        try:
            res = await tg_update_handler(*args, **kwargs)
            if res is None:
                return HandlerResult(continue_to_other_handlers=True)
            res.continue_to_other_handlers = True
            return res
        except Exception:
            logger.exception(
                f"Error processing update ({args}, {kwargs}) with handler, continuing to other handlers anyway"
            )
            return HandlerResult(continue_to_other_handlers=True)

    return wrapper
