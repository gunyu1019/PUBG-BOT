from discord.ext import interaction

from module import pubgpy


class Stats:
    def __init__(
            self,
            ctx: interaction.ApplicationContext,
            client: interaction.Client,
            pubg_client: pubgpy.Client,
            player: pubgpy.Player,
            season: pubgpy.Season,
            fpp: bool = False
    ):
        self.context = ctx
        self.client = client
        self.pubg_client = pubg_client
        self.player = player
        self.season = season
        self.fpp = fpp

    async def ranked_stats(self):

        return

    async def normal_stats(self):
        return
