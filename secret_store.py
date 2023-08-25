from pathlib import Path

from telebot_components.utils.secrets import (
    RedisSecretStore,
    SecretStore,
    TomlFileSecretStore,
)

import config
from global_redis import GLOBAL_REDIS

secret_store: SecretStore = (
    RedisSecretStore(
        redis=GLOBAL_REDIS,
        encryption_key=str(config.SECRETS_ENCRYPTION_KEY),
        secret_max_len=config.SECRET_MAX_LEN,
        secrets_per_user=config.SECRETS_PER_REGULAR_USER_QUOTA,
        scope_secrets_to_user=config.IS_PROD,
    )
    if config.IS_HEROKU
    else TomlFileSecretStore(path=Path(__file__).parent.parent / "secrets.toml")
)
