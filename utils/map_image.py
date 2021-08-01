import json
from aiohttp import ClientSession
from PIL import Image

from module import pubgpy
from utils.directory import directory

with open(f"{directory}/data/mapFileName.json") as f:
    map_file_name = json.load(f)
with open(f"{directory}/data/mapSize.json") as f:
    map_size = json.load(f)


class MapData:
    def __init__(self, map_name: pubgpy.MapName, player_id: str, data: dict = None):
        self.map = map_name
        self.map_file = Image.open(f"{directory}/assets/Maps/{map_file_name.get(self.map.value)}_Main_No_Text_Low_Res.png")
        self.data = data
        self.player_id = player_id

        self.default_map_size = 102000
        self.map_size_x = self.default_map_size * map_size.get(self.map.value, 0)
        self.map_size_y = self.default_map_size * map_size.get(self.map.value, 0)

        self.file_size_x = self.map_file.size[0]
        self.file_size_y = self.map_file.size[1]
        self.file = None
        self.init()

    async def get_assets(self, link: str):
        async with ClientSession() as session:
            async with session.request(method="GET", url=link) as resp:
                self.data = await resp.json()
        return

    def init(self):
        self.file = Image.new("RGBA", self.map_file.size)
        self.file.paste(self.map_file, (0, 0))

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

    def process(self, kill: bool = True, revive: bool = False, carepackage: bool = False):
        for data in self.data:
            if data.get("_T") == "LogPlayerKillV2" and kill:
                killer = data.get("killer", {}) if data.get("killer", {}) is not None else {}
                victim = data.get("victim", {}) if data.get("victim", {}) is not None else {}
                if killer.get("accountId", "") == self.player_id:
                    position = self._get_location(killer.get("location"))
                    _kill = Image.open(f"{directory}/assets/kill.png")
                    self.add_icon(_kill, position[0], position[1])
                elif victim.get("accountId", "") == self.player_id:
                    position = self._get_location(victim.get("location"))
                    death = Image.open(f"{directory}/assets/death.png")
                    self.add_icon(death, position[0], position[1])
        return

    def open(self):
        """For Debug"""
        self.file.show()
