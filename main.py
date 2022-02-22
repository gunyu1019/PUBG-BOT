import os

import discord
from discord.ext import interaction

from config.config import parser
from config.log_config import log

from utils.token import token

if __name__ == "__main__":
    directory = os.path.dirname(os.path.abspath(__file__))

    log.info("PUBG BOT을 불러오는 중입니다.")
    # default_prefix = ('<@!704683198164238446>', '<@704683198164238446>')
    default_prefix = "!"
    if parser.getboolean("DEFAULT", "AutoShard"):
        log.info("Config 파일에서 AutoShard가 켜져있습니다. AutoShard 기능을 킵니다.")
        bot = interaction.AutoShardedClient(
            command_prefix=default_prefix,
            intents=discord.Intents.default(),
            enable_debug_events=True,
            global_sync_command=True
        )
    else:
        bot = interaction.Client(
            command_prefix=default_prefix,
            intents=discord.Intents.default(),
            enable_debug_events=True,
            global_sync_command=True
        )

    bot.load_extensions('cogs', directory)
    bot.load_extensions('tasks', directory)
    bot.run(token)
