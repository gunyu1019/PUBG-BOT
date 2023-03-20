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
import os
import io
from PIL import Image, ImageDraw

from config.config import get_config
from module import pubgpy
from utils.directory import directory

map_setting = get_config('map_setting')


class MapAssets:
    def __init__(self, map_name: pubgpy.MapName, player_id: str, data: dict = None):
        self.map = map_name
        self.map_file = Image.open(
            os.path.join(
                directory,
                "assets",
                "maps",
                map_setting.get("MapName", str(self.map.value)) + "_Main_Low_Res.png"
            )
        )
        self.data = data
        self.player_id = player_id

        self.default_map_size = 102000
        self.map_size_x = self.default_map_size * map_setting.getint("MapSize", str(self.map.value), fallback=0)
        self.map_size_y = self.default_map_size * map_setting.getint("MapSize", str(self.map.value), fallback=0)

        self.file_size_x = self.map_file.size[0]
        self.file_size_y = self.map_file.size[1]
        self.file = None
        self.file_draw = None

        self.init()

    def init(self):
        self.file = Image.new("RGBA", self.map_file.size)
        self.file.paste(self.map_file, (0, 0))
        self.file_draw = ImageDraw.Draw(self.file, mode="RGBA")

    @staticmethod
    def _map(x, input_min, input_max, output_min, output_max) -> int:
        return int((x - input_min) * (output_max - output_min) / (input_max - input_min) + output_min)

    @staticmethod
    def _get_location(data: dict):
        return data.get("x"), data.get("y"), data.get("z")

    def add_icon(self, image, x: int, y: int):
        x_pic = self._map(x, 0, self.map_size_x, 0, self.file_size_x)
        y_pic = self._map(y, 0, self.map_size_y, 0, self.file_size_y)
        image = image.convert("RGBA").resize((40, 40))
        self.file.paste(image, (x_pic, y_pic), mask=image)

    def add_line(self, x1: int, y1: int, x2: int, y2: int, width: int = 3, color="red"):
        position_xy = [
            self._map(p, 0, self.map_size_x, 0, self.file_size_x)
            for p in (x1, y1, x2, y2)
        ]
        self.file_draw.line(position_xy, width=width, fill=color)

    def process(self, **options: bool):
        care_package_unique = []
        player_position_route = []
        for data in self.data:
            if data.get("_T") == "LogPlayerKillV2" and options.get("kill", False):
                killer = data.get("killer", {}) if data.get("killer", {}) is not None else {}
                victim = data.get("victim", {}) if data.get("victim", {}) is not None else {}
                if killer.get("accountId", "") == self.player_id:
                    position = self._get_location(killer.get("location"))
                    _kill = Image.open(os.path.join(directory, "assets", "icons", "kill.png"))
                    self.add_icon(_kill, position[0], position[1])
                elif victim.get("accountId", "") == self.player_id:
                    position = self._get_location(victim.get("location"))
                    death = Image.open(os.path.join(directory, "assets", "icons", "death.png"))
                    self.add_icon(death, position[0], position[1])
            elif data.get("_T") == "LogPlayerRevive" and options.get("revive", False):
                reviver = data.get("reviver", {}) if data.get("reviver", {}) is not None else {}
                if reviver.get("accountId", "") == self.player_id and options.get("revive", False):
                    position = self._get_location(reviver.get("location"))
                    _revive = Image.open(os.path.join(directory, "assets", "icons", "revive.png"))
                    self.add_icon(_revive, position[0], position[1])
            elif data.get("_T") == "LogItemPickupFromCarepackage" and options.get("care_package", False):
                character = data.get("character", {}) if data.get("character", {}) is not None else {}
                _care_package = data.get("carePackageUniqueId", -1)
                if character.get("accountId", "") == self.player_id and _care_package not in care_package_unique:
                    care_package_unique.append(_care_package)
                    position = self._get_location(character.get("location"))
                    _cargo = Image.open(os.path.join(directory, "assets", "icons", "care_package.png"))
                    self.add_icon(_cargo, position[0], position[1])
            elif data.get("_T") == "LogPlayerPosition" and options.get("route", False):
                character = data.get("character", {}) if data.get("character", {}) is not None else {}
                common = data.get("common", {})
                if character.get("accountId", "") == self.player_id and float(common.get("isGame", 0.0)) > 0.2:
                    position = self._get_location(character.get("location"))
                    player_position_route.append(position)
        for index, position in enumerate(player_position_route[0:-1]):
            self.add_line(
                position[0],
                position[1],
                player_position_route[index+1][0],
                player_position_route[index+1][1],
                color="#ee000080"
            )
        return

    def show(self):
        """For Debug"""
        self.file.show()

    def save(self):
        buf = io.BytesIO()
        self.file.save(buf, format='png')
        buf.seek(0)
        return buf
