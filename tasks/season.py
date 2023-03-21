import datetime
import logging
from typing import Optional

from discord.ext import interaction
from discord.ext import tasks
from sqlalchemy.ext.asyncio import AsyncResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from sqlalchemy.sql import update

from config.config import get_config
from models import database
from module import pubgpy

log = logging.getLogger(__name__)
parser = get_config()


class SeasonTask:
    def __init__(self, client: interaction.Client, factory: sessionmaker):
        self.client = client
        self.client.add_setup_hook(self.setup_hook)
        self.pubgpy = pubgpy.Client(token=parser.get("Default", "pubg_token"))
        self.factory = factory

    async def setup_hook(self):
        self.season_check.start()

    @tasks.loop(minutes=300)
    async def season_check(self):
        now = datetime.date.today()
        session: AsyncSession = self.factory.__call__()

        query = select(database.CurrentSeasonInfo)
        data: AsyncResult = await session.execute(query)
        platform_data: list[database.CurrentSeasonInfo] = data.scalars().all()
        is_commit = False

        for platform in platform_data:
            date_today = datetime.date.today()
            if (date_today - platform.last_update).days > 2:
                log.info(f"{platform.platform.value} 시즌 정보를 확인합니다.")
                self.pubgpy.platform(platform.platform)
                try:
                    season_info: list[pubgpy.Season] = await self.pubgpy.seasons()
                except pubgpy.TooManyRequests:
                    continue

                current_season: Optional[pubgpy.Season] = None
                for season in season_info:
                    if season.current:
                        current_season = season
                        break

                if current_season.id != platform.season:
                    await session.execute(
                        update(database.CurrentSeasonInfo)
                        .where(database.CurrentSeasonInfo.platform == platform.platform)
                        .values(season=current_season.id, last_update=date_today)
                    )
                    is_commit = True
                    log.info(
                        f"{platform.platform.value} 시즌 정보이 업데이트 되었습니다. ({current_season.id})"
                    )

        if is_commit:
            await session.commit()
        await session.close()
        return


def setup(client: interaction.Client, factory: sessionmaker):
    client.add_interaction_cog(SeasonTask(client, factory))
