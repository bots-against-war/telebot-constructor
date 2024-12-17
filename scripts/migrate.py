"""
Migration script to move bots from one deployment to another.

Requires yarb-against-war Python package and redis-cli installed
"""

import asyncio
import collections
import json
import logging
import os
import subprocess
import time
from pathlib import Path
from typing import cast
from urllib.parse import urlparse

import yarb  # type: ignore
from redis.asyncio import Redis  # type: ignore
from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.generic import KeyDictStore
from telebot_components.utils.secrets import RedisSecretStore

from telebot_constructor.constants import CONSTRUCTOR_PREFIX
from telebot_constructor.store.types import BotVersion


async def redis_from_environ(envname: str) -> tuple[RedisInterface, str]:
    redis_url_str = os.environ.get(envname)
    if redis_url_str is None:
        raise RuntimeError(f"Env var {envname} must be defined")
    if redis_url_str.startswith("rediss"):
        redis_url = urlparse(redis_url_str)
        r = Redis(
            host=redis_url.hostname or "",
            port=redis_url.port or 0,
            username=redis_url.username,
            password=redis_url.password,
            ssl=True,
            ssl_cert_reqs=None,  # type: ignore
        )
    else:
        r = Redis.from_url(redis_url_str)
    print(f"Pinging {envname}...")
    start = time.time()
    await r.ping()
    print(f"{envname} Redis pinged in {time.time() - start:.3f} sec")
    return cast(RedisInterface, r), redis_url_str


def running_version_store(redis: RedisInterface) -> KeyDictStore[BotVersion]:
    return KeyDictStore[BotVersion](
        name="running-version",
        prefix=CONSTRUCTOR_PREFIX,
        redis=redis,
        expiration_time=None,
    )


REDIS_DUMP_FILENAME = "dump.rdb"
SECRETS_DUMP_FILENAME = "secrets-dump.json"


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    old_encryption_key = os.environ["OLD_SECRETS_ENCRYPTION_KEY"]
    new_encryption_key = os.environ["NEW_SECRETS_ENCRYPTION_KEY"]

    new_redis_env_name = "NEW_REDIS_URL"
    new_redis, new_redis_url = await redis_from_environ(new_redis_env_name)

    old_redis_env_name = "OLD_REDIS_URL"
    old_redis, old_redis_url = await redis_from_environ(old_redis_env_name)

    redis_cli_ver_res = subprocess.run(["redis-cli", "--version"], capture_output=True)
    logging.info(f"Found Redis CLI: {redis_cli_ver_res.stdout.decode().strip()}")

    ############
    # APP DATA #
    ############
    if Path(REDIS_DUMP_FILENAME).exists():
        logging.info(f"{REDIS_DUMP_FILENAME} exists - will load data from it")
    else:
        logging.info(f"Dumping all constructor-specific keys from the old DB to {REDIS_DUMP_FILENAME}")
        await yarb.yarb_run(
            redis_url=old_redis_url,
            output_filename=REDIS_DUMP_FILENAME,
            options=yarb.YarbOptions(
                keys_match=CONSTRUCTOR_PREFIX + "*",
                # adjust according to your Redis deployment setup
                db=0,
                workers=4,
                scan_batch_size=100,
                cmd_batch_size=1000,
            ),
        )
        logging.info("Done")

    logging.info("Loading dumped keys into new redis")
    with open(REDIS_DUMP_FILENAME, "r") as stdin:
        tls_opts: list[str] = []
        if new_redis_url.startswith("rediss"):
            tls_opts.append("--tls")
            tls_opts.append("--insecure")
        parsed = urlparse(new_redis_url)
        subprocess.run(
            [
                "redis-cli",
                "--pipe",
                "-h",
                parsed.hostname or "localhost",
                "-p",
                str(parsed.port or 0),
                *tls_opts,
            ],
            stdin=stdin,
            check=True,
            env={"REDISCLI_AUTH": parsed.password or "", **os.environ},
        )
    logging.info("Redis CLI completed")

    ###########
    # SECRETS #
    ###########
    secrets_file = Path(SECRETS_DUMP_FILENAME)
    secrets: dict[str | int, dict[str, str]]
    if secrets_file.exists():
        logging.info(f"{SECRETS_DUMP_FILENAME} exists - will load secrets from it")
        secrets = json.loads(secrets_file.read_text())
    else:
        logging.info("Dumping and decoding old secretes")
        old_secret_store = RedisSecretStore(
            redis=old_redis,
            encryption_key=old_encryption_key,
            secret_max_len=10 * 1024,
            secrets_per_user=100,
            scope_secrets_to_user=True,
        )
        secret_owners = await old_secret_store.list_owners()
        logging.info(f"Old secret store has {len(secret_owners)} owners")
        secrets = collections.defaultdict(dict)
        for owner in secret_owners:
            secret_names = await old_secret_store.list_secrets(owner)
            logging.info(f"{owner} has {len(secret_names)} secrets")
            for secret_name in secret_names:
                secrets[owner][secret_name] = await old_secret_store.get_required_secret(secret_name, owner_id=owner)
        secrets_file.write_text(json.dumps(secrets))

    logging.info("Loading secrets into a new secret store")
    new_secret_store = RedisSecretStore(
        redis=new_redis,
        encryption_key=new_encryption_key,
        secret_max_len=10 * 1024,
        secrets_per_user=100,
        scope_secrets_to_user=True,
    )
    for owner, owner_secrets in secrets.items():
        logging.info(f"{owner} -> {len(owner_secrets)} secrets")
        for secret_name, secret in owner_secrets.items():
            logging.info(f"Loading {secret_name}...")
            res = await new_secret_store.save_secret(secret_name=secret_name, secret_value=secret, owner_id=owner)
            logging.info(str(res))

    ################################
    # STOPPING OLD DEPLOYMENT BOTS #
    ################################
    old_running_version_store = running_version_store(old_redis)
    owners = await old_running_version_store.list_keys()
    logging.info(f"Old store has {len(owners)} owners with some running bots")
    for owner in owners:
        bots = await old_running_version_store.list_subkeys(owner)
        logging.info(f"Turning off {owner}'s bots: {bots}")
        for bot in bots:
            await old_running_version_store.remove_subkey(owner, bot)

    logging.info("DONE! Restart the old deployment, then the new one")


if __name__ == "__main__":
    asyncio.run(main())
