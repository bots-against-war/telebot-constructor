import base64
import datetime
import enum
import hashlib
from typing import Optional

from pydantic import BaseModel
from telebot import types as tg
from telebot_components.language import any_text_to_str
from telebot_components.stores.generic import KeyValueStore
from telebot.types import InputMediaPhoto


from telebot_constructor.user_flow.blocks.base import UserFlowBlock
from telebot_constructor.user_flow.types import (
    SetupResult,
    UserFlowBlockId,
    UserFlowContext,
    UserFlowSetupContext,
)
from telebot_constructor.utils import without_nones
from telebot_constructor.utils.pydantic import (
    ExactlyOneNonNullFieldModel,
    LocalizableText,
)


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
    text: LocalizableText
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

    def possible_next_block_ids(self) -> list[str]:
        return without_nones([self.next_block_id])

    # TODO:
    # - validation on input (text length and markup validity, content base64 encoding, etc)
    # - splitting long text content into smaller content chunks to respect telegram's restrictions

    @classmethod
    def simple_text(
        cls, block_id: str, message_text: LocalizableText, next_block_id: Optional[UserFlowBlockId]
    ) -> "ContentBlock":
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
        language = (
            await self._language_store.get_user_language(context.user) if self._language_store is not None else None
        )
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
                        text=any_text_to_str(content.text.text, language),
                        **common_kwargs,  # type: ignore
                    )
                else:
                    # TODO: empty block (no text, no attachments) should be a validation error
                    pass
            elif len(content.attachments) == 1:
                common_kwargs = common_kwargs.copy()
                if content.text is not None:
                    common_kwargs["caption"] = any_text_to_str(content.text.text, language)
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
                common_kwargs = common_kwargs.copy()
                if content.text is not None:
                    common_kwargs["caption"] = any_text_to_str(content.text.text, language)
                attachments = content.attachments
                media_group = []
                flag_content = None
                for attachment in attachments:
                    # TODO: generalize on other attachment types
                    if attachment.image is not None:
                        file_id = await self._file_id_by_hash_store.load(md5_hash(attachment.image))
                        if file_id is not None:
                            media_group.append(
                                InputMediaPhoto(file_id),
                                **common_kwargs if flag_content == None else None,  # type: ignore
                            )
                            flag_content = "not send"
                        else:
                            media_group = []  # clear media group, becouse one if file dosn't in cash
                            flag_content = None
                            for attachment in attachments:
                                media_group.append(
                                    InputMediaPhoto(attachment),
                                    **common_kwargs if flag_content == None else None,  # type: ignore
                                )
                                flag_content = "not send"
                            msg_group = await context.bot.send_media_group(media_group)
                            for attachment, msg in zip(attachments, msg_group):
                                file_id = msg.photo[0].file_id
                                await self._file_id_by_hash_store.save(md5_hash(attachment.image), file_id)
                            break

                await context.bot.send_media_group(media_group)

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

        self._language_store = context.language_store
        return SetupResult.empty()


def md5_hash(data: str) -> str:
    return hashlib.md5(data.encode("utf-8"), usedforsecurity=False).hexdigest()
