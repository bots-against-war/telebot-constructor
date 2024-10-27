import base64
import datetime
import hashlib
import logging
import re
from typing import Any, Optional

from pydantic import BaseModel
from telebot import types as tg
from telebot_components.language import any_text_to_str, vaildate_singlelang_text
from telebot_components.stores.generic import KeyValueStore
from telebot_components.utils import TextMarkup

from telebot_constructor.user_flow.blocks.base import UserFlowBlock
from telebot_constructor.user_flow.types import (
    SetupResult,
    UserFlowBlockId,
    UserFlowContext,
    UserFlowSetupContext,
)
from telebot_constructor.utils import (
    iter_batches,
    preprocess_for_telegram,
    without_nones,
)
from telebot_constructor.utils.pydantic import (
    ExactlyOneNonNullFieldModel,
    LocalizableText,
)

logger = logging.getLogger(__name__)


class ContentText(BaseModel):
    text: LocalizableText
    markup: TextMarkup

    _preprocessed_text: LocalizableText | None = None

    @property
    def preprocessed(self) -> LocalizableText:
        return self._preprocessed_text or self.text

    def model_post_init(self, __context: Any) -> None:
        self._preprocessed_text = preprocess_for_telegram(self.text, self.markup)

    def is_empty(self) -> bool:
        if isinstance(self.text, str):
            return len(self.text) == 0
        else:
            return any(len(v) == 0 for v in self.text.values())


class ContentBlockContentAttachment(ExactlyOneNonNullFieldModel):
    image: Optional[str]  # base64-encoded with possible "data:*/*;base64," prefix
    filename: str = ""

    def content(self) -> str:
        # runtime guarantee that at least one (now it's always image) option is non-None
        return self.image  # type: ignore


data_url_prefix_re = re.compile(r"^data:\w+/\w+;base64,")


def decode_b64_data_url(b64_data_url: str) -> bytes:
    print(b64_data_url[:64])
    return base64.b64decode(data_url_prefix_re.sub("", b64_data_url))


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

    def model_post_init(self, __context: Any) -> None:
        if not self.contents:
            raise ValueError("Block must contain at least one content unit")
        empty_contents = [c for c in self.contents if (c.text is None or c.text.is_empty()) and not c.attachments]
        if empty_contents:
            raise ValueError(f"Block contains empty content unit(s): {len(empty_contents)}")
        contents_validated: list[Content] = []
        for c in self.contents:
            # checking for too long captions (too long texts are split automatically by telebot library)
            # limit is 1024 symbols, see docs: https://core.telegram.org/bots/api#inputmediaphoto
            # note that we are here conservative as we includes e.g. HTML markup in the symbol bugdet
            if c.attachments and c.text is not None and len(c.text.preprocessed) > 1024:
                # splitting long text and attachments into separate units
                contents_validated.append(Content(text=c.text, attachments=[]))
                c = Content(text=None, attachments=c.attachments)

            # checking for too many attachments
            if len(c.attachments) > 10:
                batches = list(iter_batches(c.attachments, size=10))
                contents_validated.append(Content(text=c.text, attachments=batches[0]))
                contents_validated.extend(Content(text=None, attachments=batch) for batch in batches[1:-1])
                c = Content(text=None, attachments=batches[-1])

            # when we support multiple attachment types, we should also check attachment compatibility
            # (e.g. photo + audio is disallowed)

            contents_validated.append(c)

        self.contents = contents_validated

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
                        markup=TextMarkup.NONE,
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
        for content in self.contents:
            parse_mode = content.text.markup.parse_mode() if content.text is not None else None
            if not content.attachments:
                if content.text is not None:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=any_text_to_str(content.text.preprocessed, language),
                        parse_mode=parse_mode,
                        reply_markup=tg.ReplyKeyboardRemove(),
                    )
                else:
                    logger.error("Empty content block: no text and no attachments!")
            elif len(content.attachments) == 1:
                attachment = content.attachments[0]
                if attachment.image is not None:
                    file_id = await self._file_id_by_hash_store.load(md5_hash(attachment.image))
                    message = await context.bot.send_photo(
                        chat_id=chat_id,
                        photo=file_id if file_id is not None else decode_b64_data_url(attachment.image),
                        caption=(
                            any_text_to_str(content.text.preprocessed, language) if content.text is not None else None
                        ),
                        parse_mode=parse_mode if content.text is not None else None,
                        reply_markup=tg.ReplyKeyboardRemove(),
                    )
                    if file_id is None:
                        if message.photo is not None:
                            file_id = message.photo[0].file_id
                            await self._file_id_by_hash_store.save(md5_hash(attachment.image), file_id)
                        else:
                            logger.error(
                                "Telegram unexpectedly returned message without photo on send_photo, "
                                + "unable to fill the cache"
                            )
                else:
                    logger.error("Unexpected attachment type; only images are supported for now")
            else:  # multiple attachments case
                logger.debug("Sending message with multiple attachments")
                attachment_md5_hashes = [md5_hash(att.content()) for att in content.attachments]
                cached_file_ids = [await self._file_id_by_hash_store.load(att_md5) for att_md5 in attachment_md5_hashes]
                logger.debug(f"Found file ids in cache (None = cache miss): {cached_file_ids}")

                media = [
                    (
                        tg.InputMediaPhoto(maybe_file_id)  # type: ignore
                        if maybe_file_id is not None
                        else tg.InputMediaPhoto(decode_b64_data_url(attachment.image))  # type: ignore
                    )
                    for maybe_file_id, attachment in zip(cached_file_ids, content.attachments)
                ]
                # for media groups, text content is put to first media's caption
                if content.text is not None:
                    media[0].caption = any_text_to_str(content.text.preprocessed, language)
                    media[0].parse_mode = parse_mode
                    # NOTE: reply markup is not available for media groups, so we don't send it

                messages = await context.bot.send_media_group(
                    chat_id=chat_id,
                    media=list(media),  # <- hack to get over bad upstream lib typing
                )
                logger.debug(f"Sent media group, received messages: {messages}")

                if len(messages) != len(content.attachments):
                    logger.error(
                        "send_media_group returned unexpected number of messages "
                        + f"({len(messages) = }, {len(content.attachments) = })"
                    )
                for message, cached_file_id, attachment_md5 in zip(messages, cached_file_ids, attachment_md5_hashes):
                    if cached_file_id is not None:
                        continue
                    if message.photo is None:
                        logger.error(
                            "Telegram unexpectedly returned message without photo on send_photo, "
                            + "unable to fill the cache, ignoring it"
                        )
                        continue

                    file_id = message.photo[0].file_id
                    logger.debug(f"Saving attachment file id to cache: {attachment_md5} -> {file_id}")
                    await self._file_id_by_hash_store.save(attachment_md5, file_id)

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
        # validating texts against language store
        for c in self.contents:
            if c.text is None:
                continue
            if self._language_store is not None:
                self._language_store.validate_multilang(c.text.preprocessed)
            else:
                vaildate_singlelang_text(c.text.preprocessed)

        return SetupResult.empty()


def md5_hash(data: str) -> str:
    return hashlib.md5(data.encode("utf-8"), usedforsecurity=False).hexdigest()
