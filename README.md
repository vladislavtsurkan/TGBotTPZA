## Telegram Bot for watching the schedule of the Kyiv Polytechnic Institute
This is a bot for [Telegram](https://telegram.org/) written on [Aiogram](https://docs.aiogram.dev/en/latest/).

List of libraries I used:
- [aiogram](https://docs.aiogram.dev/en/latest/)
- [sqlalchemy](https://docs.sqlalchemy.org/en/14/)
- [alembic](https://alembic.sqlalchemy.org/en/latest/)
- [aiohttp](https://docs.aiohttp.org/en/stable/)
- [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [lxml](https://lxml.de/)
- [pytest](https://docs.pytest.org/en/6.2.x/)
- [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio)


To start using the bot you should set the next **_environment variables_** in your system:
```
BOT_TOKEN = <your_bot_token>
DB_HOST = <mysql_db_host>
DB_USER = <mysql_db_user>
DB_PASSWORD = <mysql_db_password>
DB_NAME = <mysql_db_name>
MONGO_DB_HOST = <mongo_db_host>
MONGO_DB_NAME = <mongo_db_name>
MONGO_DB_PORT = <mongo_db_port>
```
For install all dependencies you should run the next command:
```bash
pip install -r requirements.txt
```
For start bot you should run next command:
```bash
python3 main.py
```
Also, you can use **docker-compose** for run the bot. For this, you should edit in the **_docker-compose.yml_** 
environment variable `BOT_TOKEN` and start the docker-compose:
```bash
docker-compose up -d
```
> **Authors:** 
> - [Vladyslav Tsurkan](https://t.me/vladyslavtsurkan)
> - [Tetyana Savchenko](https://t.me/leasael)