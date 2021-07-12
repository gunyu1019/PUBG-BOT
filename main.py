import os
import discord
from discord.ext import commands

from config.config import parser
from config.log_config import log

from utils.prefix import get_prefix
from utils.token import token

if __name__ == "__main__":
    directory = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")

    log.info("PUBG BOT을 불러오는 중입니다.")
    if parser.getboolean("DEFAULT", "AutoShard"):
        log.info("Config 파일에서 AutoShard가 켜져있습니다. AutoShard 기능을 킵니다.")
        bot = commands.AutoShardedBot(command_prefix=get_prefix)
    else:
        bot = commands.Bot(command_prefix=get_prefix, intents=discord.Intents.all())

    bot.remove_command("help")
    cogs = ["cogs." + file[:-3] for file in os.listdir(f"{directory}/cogs") if file.endswith(".py")]
    for cog in cogs:
        bot.load_extension(cog)

    bot.run(token)
