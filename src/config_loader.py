from typing import NamedTuple
from os import getenv


class BotConfig(NamedTuple):
    token: str


class DatabaseConfig(NamedTuple):
    host: str
    db_name: str
    user: str
    password: str


class RedisConfig(NamedTuple):
    host: str
    port: int
    password: str
    db: int = 0


def load_config_db() -> DatabaseConfig:
    return DatabaseConfig(
        host=getenv("DB_HOST"),
        db_name=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASS")
    )


def load_config_redis() -> RedisConfig:
    return RedisConfig(
        host=getenv("REDIS_HOST"),
        port=int(getenv("REDIS_PORT")),
        password=getenv("REDIS_PASS"),
    )


def load_config_bot() -> BotConfig:
    return BotConfig(
        token=getenv("BOT_TOKEN")
    )
