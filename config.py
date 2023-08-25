import os

IS_HEROKU = bool(os.environ.get("IS_HEROKU", False))
IS_PROD = bool(os.environ.get("IS_PRODUCTION", False))

ENVIRONMENT = "prod" if IS_PROD else ("stage" if IS_HEROKU else "local")
RELEASE = os.environ.get("HEROKU_RELEASE_VERSION", "<no-release>")
COMMIT = os.environ.get("HEROKU_SLUG_COMMIT", "<no-commit>")
DESCRIPTION = os.environ.get("HEROKU_SLUG_DESCRIPTION", "<no-description>")

REDIS_URL = os.environ.get("REDIS_URL")

SECRETS_ENCRYPTION_KEY = os.environ.get("SECRETS_ENCRYPTION_KEY")
SECRETS_PER_REGULAR_USER_QUOTA = int(os.environ.get("SECRETS_PER_USER", 10))
SECRET_MAX_LEN = int(os.environ.get("SECRET_MAX_LEN", 10 * 1024))

# no trailing slash, e.g. https://bots-against-war.herokuapp.com
LOCALHOST_URL = "localhost:8088"
PUBLIC_URL = os.environ.get("PUBLIC_URL", LOCALHOST_URL)

# set by heroku automatically
PORT = os.environ.get("PORT", 8088)

if IS_HEROKU:
    if REDIS_URL is None:
        raise SystemExit("REDIS_URL env var must be specified when deploying to Heroku")
    if SECRETS_ENCRYPTION_KEY is None:
        raise SystemExit("SECRETS_ENCRYPTION_KEY env var must be specified when deploying to Heroku")
