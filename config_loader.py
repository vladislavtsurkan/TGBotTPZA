from typing import NamedTuple
from os import getenv


class Bot(NamedTuple):
    token: str


class DB(NamedTuple):
    host: str
    db_name: str
    user: str
    password: str


class Config(NamedTuple):
    bot: Bot
    db: DB


def load_config():
    return Config(
        bot=Bot(token=getenv("BOT_TOKEN")),
        db=DB(
            host=getenv("DB_HOST"),
            db_name=getenv("DB_NAME"),
            user=getenv("DB_USER"),
            password=getenv("DB_PASS")
        )
    )
