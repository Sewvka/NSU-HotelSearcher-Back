"""File with settings and configs for the project"""

from envparse import Env

env = Env()

ACCESS_TOKEN_EXPIRE_MINUTES: int = env.int("ACCESS_TOKEN_EXPIRE_MINUTES", default=30)
SECRET_KEY: str = env.str("SECRET_KEY", default="secret_key")
ALGORITHM: str = env.str("ALGORITHM", default="HS256")
CRONITOR_API_KEY: str = env.str("CRONITOR_API_KEY", default="7d223f7a46664253989cf04f32b30774")

REAL_DATABASE_URL = env.str(
    "REAL_DATABASE_URL",
    default='postgresql+asyncpg://postgres:postgres@25.56.214.53:5432/postgres'
)

REAL_DATABASE_URL_CEL = env.str(
    "REAL_DATABASE_URL_CEL",
    default='postgresql://postgres:postgres@25.56.214.53:5432/postgres'
)

REDIS_BROKER_URL: str = env.str(
    "REDIS_BROKER_URL",
    default="redis://25.56.214.53:6379/0"
)

TEST_DATABASE_URL = env.str(
    "TEST_DATABASE_URL",
    default='postgresql+asyncpg://postgres_test:postgres_test@127.0.0.1:5433/postgres_test'
)