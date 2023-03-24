import datetime

from discord.ext import interaction
from sqlalchemy.ext.asyncio import AsyncResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import delete
from sqlalchemy.sql import exists
from sqlalchemy.sql import select

from models import database
from module import pubgpy


class FavoriteBasic:
    def __init__(
        self,
        ctx: interaction.ApplicationContext,
        client: interaction.Client,
        factory: sessionmaker,
        player: pubgpy.Player,
    ):
        self.context = ctx
        self.player = player
        self.factory = factory

        self.is_favorite = None
        super().__init__(ctx, client)

    async def load_favorite(self, session: AsyncSession = None) -> bool:
        only_session = False
        if session is None:
            only_session = True
            session = self.factory.__call__()

        query = select(
            exists(database.FavoritePlayer).where(
                (database.FavoritePlayer.player_id == self.player.id)
                & (database.FavoritePlayer.discord_id == self.context.author.id)
            )
        )
        data: AsyncResult = await session.execute(query)
        self.is_favorite = result = data.scalar_one_or_none()
        if result is None:
            result = False

        if only_session:
            await session.close()
        return result

    async def update_favorite(self, session: AsyncSession = None):
        only_session = False
        if session is None:
            only_session = True
            session = self.factory.__call__()

        if self.is_favorite is None:
            self.is_favorite = await self.load_favorite(session)

        match self.is_favorite:
            case False:
                data = database.FavoritePlayer(
                    idx=int(datetime.datetime.now().timestamp() * 1000000),
                    player_id=self.player.id,
                    discord_id=self.context.author.id,
                )
                session.add(data)
            case True:
                query = delete(database.FavoritePlayer).where(
                    (database.FavoritePlayer.discord_id == self.context.id)
                    & (database.FavoritePlayer.player_id == self.player.id)
                )
                await session.execute(query)
        self.is_favorite = not self.is_favorite

        if only_session:
            await session.commit()
            await session.close()
