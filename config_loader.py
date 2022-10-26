from typing import NamedTuple
from os import getenv


class Bot(NamedTuple):
    token: str


class DB(NamedTuple):
    host: str
    db_name: str
    user: str
    password: str


def load_config_db() -> DB:
    return DB(
        host=getenv("DB_HOST"),
        db_name=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASS")
    )


def load_config_bot() -> Bot:
    return Bot(
        token=getenv("BOT_TOKEN")
    )
