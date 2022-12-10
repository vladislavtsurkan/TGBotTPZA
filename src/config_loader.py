from typing import NamedTuple
from os import getenv


class BotConfig(NamedTuple):
    token: str


class DatabaseConfig(NamedTuple):
    host: str
    db_name: str
    user: str
    password: str


class MongoDBConfig(NamedTuple):
    host: str
    port: int
    db_name: str


def load_config_db() -> DatabaseConfig:
    return DatabaseConfig(
        host=getenv("DB_HOST"),
        db_name=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASS")
    )


def load_config_mongo_db() -> MongoDBConfig:
    return MongoDBConfig(
        host=getenv("MONGO_DB_HOST"),
        port=int(getenv("MONGO_DB_PORT")),
        db_name=getenv("MONGO_DB_NAME")
    )


def load_config_bot() -> BotConfig:
    return BotConfig(
        token=getenv("BOT_TOKEN")
    )
