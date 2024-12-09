import abc
import logging
import mimetypes
import uuid
from typing import Any

import aiobotocore.client  # type: ignore
import aiobotocore.session  # type: ignore
import pydantic

logger = logging.getLogger(__name__)


class Media(pydantic.BaseModel):
    content: bytes
    filename: str | None


MediaId = str


class MediaStore(abc.ABC):
    @abc.abstractmethod
    async def save_media(self, owner_id: str, media: Media) -> MediaId | None: ...

    @abc.abstractmethod
    async def load_media(self, owner_id: str, media_id: MediaId) -> Media | None: ...

    @abc.abstractmethod
    async def delete_media(self, owner_id: str, media_id: MediaId) -> bool: ...

    async def setup(self) -> None: ...

    async def cleanup(self) -> None: ...


class AwsS3Credentials(pydantic.BaseModel):
    access_key_id: str
    secret_access_key: str
    region: str
    bucket: str


class AwsS3MediaStore(MediaStore):
    def __init__(self, credentials: AwsS3Credentials) -> None:
        self.credentials = credentials

    async def setup(self) -> None:
        session = aiobotocore.session.get_session()
        # HACK: (aio)botocore forces the use of client as a context manager, but it will not fly with us
        self.client: aiobotocore.client.AioBaseClient = await session._create_client(
            "s3",
            region_name="us-west-2",
            aws_secret_access_key=self.credentials.secret_access_key,
            aws_access_key_id=self.credentials.access_key_id,
        )
        await self.client.__aenter__()

    async def cleanup(self):
        await self.client.__aexit__(None, None, None)

    async def save_media(self, owner_id: str, media: Media) -> MediaId | None:
        media_id = str(uuid.uuid4())
        content_type: str | None = None
        if media.filename is not None:
            content_type, _ = mimetypes.guess_type(media.filename)

        # see docs at
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/put_object.html
        put_object_kwargs: dict[str, Any] = dict()
        if content_type is not None:
            put_object_kwargs["ContentType"] = content_type
        if media.filename is not None:
            put_object_kwargs["Metadata"] = {"filename": media.filename}

        try:
            resp = await self.client.put_object(
                Bucket=self.credentials.bucket,
                Key=f"{owner_id}/{media_id}",
                Body=media.content,
                **put_object_kwargs,
            )
            logging.debug("Response from S3: %s", resp)
            return media_id
        except Exception:
            logging.exception("Error putting object in S3 bucket")
            return None

    async def load_media(self, owner_id: str, media_id: MediaId) -> Media | None:
        try:
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/get_object.html
            resp = await self.client.get_object(
                Bucket=self.credentials.bucket,
                Key=f"{owner_id}/{media_id}",
            )
            body = resp["Body"]
            return Media(content=await body.read(), filename=resp.get("Metadata", {}).get("filename"))
        except Exception as exc:
            if exc.__class__.__name__ != "NoSuchKey":
                logger.exception("Unexpected error getting an object from S3")
            return None

    async def delete_media(self, owner_id: str, media_id: MediaId) -> bool:
        try:
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/delete_object.html
            await self.client.delete_object(
                Bucket=self.credentials.bucket,
                Key=f"{owner_id}/{media_id}",
            )
            return True
        except Exception as exc:
            if exc.__class__.__name__ != "NoSuchKey":
                logger.exception("Unexpected error getting an object from S3")
            return False
