import os
import discord
from discord.ext import interaction
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession

from config.config import get_config
from config.log_config import log

parser = get_config()

if __name__ == "__main__":
    directory = os.path.dirname(os.path.abspath(__file__))

    log.info("PUBG BOT을 불러오는 중입니다.")
    if parser.getboolean("Default", "AutoShard"):
        log.info("Config 파일에서 AutoShard가 켜져있습니다. AutoShard 기능을 킵니다.")
        bot = interaction.AutoShardedClient(
            intents=discord.Intents.default(),
            enable_debug_events=True,
            global_sync_command=True
        )
    else:
        bot = interaction.Client(
            intents=discord.Intents.default(),
            enable_debug_events=True,
            global_sync_command=True
        )

    # Database
    database = {
        "username": parser.get("MySQL", "user"),
        "host": parser.get("MySQL", "host"),
        "password": parser.get("MySQL", "pass"),
        "database": parser.get("MySQL", "database"),
        "port": parser.getint("MySQL", "port", fallback=3306)
    }
    engine = create_async_engine("mysql+aiomysql://{username}:{password}@{host}:{port}/{database}".format(**database))
    factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    bot.load_extensions('cogs', directory, factory=factory)
    bot.load_extensions('tasks', directory, factory=factory)
    bot.run(parser.get("Default", "token"))
