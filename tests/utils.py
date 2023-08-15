from cryptography.fernet import Fernet
from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.utils.secrets import RedisSecretStore, SecretStore


def dummy_secret_store(redis: RedisInterface) -> SecretStore:
    return RedisSecretStore(
        redis,
        encryption_key=Fernet.generate_key().decode("utf-8"),
        secrets_per_user=100,
        secret_max_len=1000,
        scope_secrets_to_user=True,
    )
