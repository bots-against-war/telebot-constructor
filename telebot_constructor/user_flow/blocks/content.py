import base64
import datetime
import enum
import hashlib
from typing import Optional

from pydantic import BaseModel
from telebot import types as tg
from telebot_components.stores.generic import GenericStore, KeyValueStore

from telebot_constructor.user_flow.blocks.base import UserFlowBlock
from telebot_constructor.user_flow.types import (
    SetupResult,
    UserFlowBlockId,
    UserFlowContext,
    UserFlowSetupContext,
)
from telebot_constructor.utils.pydantic import ExactlyOneNonNullFieldModel


class ContentTextMarkup(enum.Enum):
    NONE = "none"
    HTML = "html"
    MARKDOWN = "markdown"

    def as_parse_mode(self) -> Optional[str]:
        """See https://core.telegram.org/bots/api#formatting-options"""
        if self is ContentTextMarkup.NONE:
            return None
        elif self is ContentTextMarkup.HTML:
            return "HTML"
        elif self is ContentTextMarkup.MARKDOWN:
            return "MarkdownV2"


class ContentText(BaseModel):
    text: str
    markup: ContentTextMarkup


class ContentBlockContentAttachment(ExactlyOneNonNullFieldModel):
    image: Optional[str]  # base64-encoded


class Content(BaseModel):
    text: Optional[ContentText]
    attachments: list[ContentBlockContentAttachment]


class ContentBlock(UserFlowBlock):
    """
    Simplest user flow block: static content sent by bot in one or several telegram messages.
    Immediately continues to the next block after sending the content.
    """

    contents: list[Content]
    next_block_id: Optional[UserFlowBlockId]

    # TODO:
    # - validation on input (text length and markup validity, content base64 encoding, etc)
    # - splitting long text content into smaller content chunks to respect telegram's restrictions

    @classmethod
    def simple_text(cls, block_id: str, message_text: str, next_block_id: Optional[UserFlowBlockId]) -> "ContentBlock":
        """For use in tests"""
        return ContentBlock(
            block_id=block_id,
            contents=[
                Content(
                    text=ContentText(
                        text=message_text,
                        markup=ContentTextMarkup.NONE,
                    ),
                    attachments=[],
                )
            ],
            next_block_id=next_block_id,
        )

    async def enter(self, context: UserFlowContext) -> None:
        chat_id = context.chat.id if context.chat is not None else context.user.id
        # TODO: deal with errors?
        for content in self.contents:
            common_kwargs = {
                "chat_id": chat_id,
                "reply_markup": tg.ReplyKeyboardRemove(),
                "parse_mode": content.text.markup.as_parse_mode() if content.text is not None else None,
            }
            if not content.attachments:
                if content.text is not None:
                    await context.bot.send_message(
                        text=content.text.text,
                        **common_kwargs,  # type: ignore
                    )
                else:
                    # TODO: empty block (no text, no attachments) should be a validation error
                    pass
            elif len(content.attachments) == 1:
                common_kwargs = common_kwargs.copy()
                if content.text is not None:
                    common_kwargs["caption"] = content.text.text
                attachment = content.attachments[0]
                # TODO: generalize on other attachment types
                if attachment.image is not None:
                    file_id = await self._file_id_by_hash_store.load(md5_hash(attachment.image))
                    if file_id is not None:
                        await context.bot.send_photo(
                            photo=file_id,
                            **common_kwargs,  # type: ignore
                        )
                    else:
                        photo_bytes = base64.b64decode(attachment.image)
                        msg = await context.bot.send_photo(
                            photo=photo_bytes,
                            **common_kwargs,  # type: ignore
                        )
                        if msg.photo is not None:
                            file_id = msg.photo[0].file_id
                            await self._file_id_by_hash_store.save(md5_hash(attachment.image), file_id)
            else:
                # TODO: use send_media_group, but validate constraints and reuse file_id caching logic from above
                context.bot.send_media_group
                raise RuntimeError("Multiple attachments per message TBD")

        if self.next_block_id is not None:
            await context.enter_block(self.next_block_id, context)

    async def setup(self, context: UserFlowSetupContext) -> SetupResult:
        self._file_id_by_hash_store = KeyValueStore[str](
            name="file-id",
            prefix=context.bot_prefix,
            redis=context.redis,
            expiration_time=datetime.timedelta(days=180),
            dumper=str,
            loader=str,
        )
        # the store can be shared between content blocks, so they can reuse cached file_id's
        GenericStore.allow_duplicate_stores(prefix=self._file_id_by_hash_store._full_prefix)
        return SetupResult.empty()


def md5_hash(data: str) -> str:
    return hashlib.md5(data.encode("utf-8"), usedforsecurity=False).hexdigest()
