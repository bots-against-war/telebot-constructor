import asyncio
import logging
import os
import sys
from pathlib import Path

from telebot_constructor.store.media import AwsS3Credentials, AwsS3MediaStore, Media

logging.basicConfig()


async def main(file_path: str) -> None:
    creds = AwsS3Credentials.model_validate_json(os.environ["MEDIA_STORE_AWS_S3_CREDENTIALS"])
    store = AwsS3MediaStore(creds)

    path = Path(file_path)
    media = Media(
        content=path.read_bytes(),
        filename=path.name,
    )

    owner = "test-owner"
    await store.setup()
    try:
        media_id = await store.save_media(owner_id=owner, media=media)
        if media_id is None:
            print("Failed to upload")
            return
        print("Got media id:", media_id)

        print("Loading back...")
        m = await store.load_media(owner_id=owner, media_id=media_id)
        if m is None:
            print("Failed to download file back")
            return

        outpath = path.with_stem("output")
        print("Writing to", outpath)
        outpath.write_bytes(m.content)
        print("Sleeping 20 sec before deleting the object")
        await asyncio.sleep(20)

        print("Deleting the object")
        is_deleted = await store.delete_media(owner, media_id)
        print("Result:", is_deleted)
    finally:
        await store.cleanup()


if __name__ == "__main__":
    file_path = sys.argv[1]
    asyncio.run(main(file_path))
