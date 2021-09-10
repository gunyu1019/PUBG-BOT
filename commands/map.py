"""GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (c) 2021 gunyu1019

PUBG BOT is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PUBG BOT is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PUBG BOT.  If not, see <http://www.gnu.org/licenses/>.
"""

import discord
import json

from config.config import parser
from module import commands
from utils.directory import directory

with open(directory + "/data/mapLink.json", mode='r') as file:
    map_link = json.load(file)


def add_map_file(map_name, embed):
    embed.clear_fields()

    map_file = map_link[map_name]
    embed.add_field(name="원본(텍스트 삭제)", value=f"[링크]({map_file['No_Text_Low_Res']})", inline=True)
    embed.add_field(name="고화질", value=f"[링크]({map_file['High_Res']})", inline=True)
    embed.add_field(name="고화질(텍스트 삭제)", value=f"[링크]({map_file['No_Text_High_Res']})", inline=True)
    embed.set_image(url=f"attachment://{map_name}_Main_Low_Res.png")


class Command:
    def __init__(self, bot):
        self.client = bot

        self.color = int(parser.get("Color", "default"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)

        self.embed = discord.Embed(title="지도", color=self.color)

    @commands.command(name="에란겔", permission=4)
    async def erangel(self, ctx):
        map_file = discord.File(directory + "/assets/Maps/Erangel_Main_Low_Res.png")
        add_map_file('Erangel', self.embed)
        await ctx.send(file=map_file, embed=self.embed)
        return

    @commands.command(name="미라마", permission=4)
    async def miramar(self, ctx):
        map_file = discord.File(directory + "/assets/Maps/Miramar_Main_Low_Res.png")
        add_map_file('Miramar', self.embed)
        await ctx.send(file=map_file, embed=self.embed)
        return

    @commands.command(name="사녹", permission=4)
    async def sanhok(self, ctx):
        map_file = discord.File(directory + "/assets/Maps/Sanhok_Main_Low_Res.png")
        add_map_file('Sanhok', self.embed)
        await ctx.send(file=map_file, embed=self.embed)
        return

    @commands.command(name="비켄디", permission=4)
    async def vikendi(self, ctx):
        map_file = discord.File(directory + "/assets/Maps/Vikendi_Main_Low_Res.png")
        add_map_file('Vikendi', self.embed)
        await ctx.send(file=map_file, embed=self.embed)
        return

    @commands.command(name="파라모", permission=4)
    async def paramo(self, ctx):
        map_file = discord.File(directory + "/assets/Maps/Paramo_Main_Low_Res.png")
        add_map_file('Paramo', self.embed)
        await ctx.send(file=map_file, embed=self.embed)
        return

    @commands.command(name="캠프자칼", permission=4)
    async def camp_jackal(self, ctx):
        map_file = discord.File(directory + "/assets/Maps/Camp_Jackal_Main_Low_Res.png")
        add_map_file('Camp_Jackal', self.embed)
        await ctx.send(file=map_file, embed=self.embed)
        return

    @commands.command(name="헤이븐", permission=4)
    async def heaven(self, ctx):
        map_file = discord.File(directory + "/assets/Maps/Haven_Main_Low_Res.png")
        add_map_file('Heaven', self.embed)
        await ctx.send(file=map_file, embed=self.embed)
        return

    @commands.command(name="테이고", permission=4)
    async def taego(self, ctx):
        map_file = discord.File(directory + "/assets/Maps/Taego_Main_Low_Res.png")
        add_map_file('Taego', self.embed)
        await ctx.send(file=map_file, embed=self.embed)
        return


def setup(client):
    return Command(client)
