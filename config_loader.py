from typing import NamedTuple
from os import getenv


class BotConfig(NamedTuple):
    token: str


class DB(NamedTuple):
    host: str
    db_name: str
    user: str
    password: str


class MongoDB(NamedTuple):
    host: str
    port: int
    db_name: str


def load_config_db() -> DB:
    return DB(
        host=getenv("DB_HOST"),
        db_name=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASS")
    )


def load_config_mongo_db() -> MongoDB:
    return MongoDB(
        host=getenv("MONGO_DB_HOST"),
        port=int(getenv("MONGO_DB_PORT")),
        db_name=getenv("MONGO_DB_NAME")
    )


def load_config_bot() -> BotConfig:
    return BotConfig(
        token=getenv("BOT_TOKEN")
    )
