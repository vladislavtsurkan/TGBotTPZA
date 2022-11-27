from typing import TypeAlias
from sqlalchemy.ext.declarative import declarative_base

from config_loader import load_config_db, DatabaseConfig

sqlalchemy_url: TypeAlias = str

Base = declarative_base()


def get_sqlalchemy_url() -> sqlalchemy_url:
    config_db: DatabaseConfig = load_config_db()
    return (
        f'mysql+asyncmy://{config_db.user}:{config_db.password}@'
        f'{config_db.host}/{config_db.db_name}'
    )
