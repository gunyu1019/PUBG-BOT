import datetime
import io
import os
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from models import database
from module.statsType import StatsPlayType
from utils.directory import directory
from utils.location import comment


class ImageProcess:
    def __init__(self, player_info: database.Player, language: str):
        self.background_canvas = Image.open(
            fp=os.path.join(directory, "assets", "background", "background_1.png")
        )
        self.background_canvas = self.background_canvas.resize((768, 433))

        self.player_name_font = ImageFont.truetype(
            os.path.join(directory, "assets", "fonts", "NotoSansKR-Black.otf"),
            size=36
        )
        self.sub_title_font = ImageFont.truetype(
            os.path.join(directory, "assets", "fonts", "TmoneyRoundWindExtraBold.otf"),
            size=16
        )
        self.sub_description_font = ImageFont.truetype(
            os.path.join(directory, "assets", "fonts", "TmoneyRoundWindExtraBold.otf"),
            size=20
        )
        self.play_time_font = ImageFont.truetype(
            os.path.join(directory, "assets", "fonts", "TmoneyRoundWindExtraBold.otf"),
            size=16
        )
        self.player = player_info
        self.language = language

    def base_canvas(self, stats: dict[StatsPlayType, database.NormalStats | database.RankedStats | None]):
        canvas = Image.new('RGBA', (768, 433))
        layout_canvas = Image.open(
            fp=os.path.join(directory, "assets", "layout", "normal_layout.png")
        )

        canvas.paste(self.background_canvas, (0, 0))
        canvas.paste(layout_canvas, (0, 0), mask=layout_canvas.split()[3])

        draw_canvas = ImageDraw.Draw(canvas)

        # Player Title
        _, player_name_text_h = draw_canvas.textsize(self.player.name, font=self.player_name_font)
        draw_canvas.text(
            (22, (80 - player_name_text_h) / 2),
            self.player.name,
            font=self.player_name_font,
            fill="#f1ca09"
        )

        # Update Date Text
        temp_game_data = stats.get(StatsPlayType.SOLO)
        update_data = temp_game_data.update_time.strftime("%Y년 %m월 %d일 %H:%M")
        draw_canvas.text(
            (30, 383), "최근 업데이트: {}".format(update_data),
            font=self.play_time_font,
            fill="#d4ddf4"
        )
        return canvas, draw_canvas

    def normal_stats(self, stats: dict[StatsPlayType, database.NormalStats | None]):
        canvas, draw_canvas = self.base_canvas(stats)

        # Solo / Duo / Squad
        for category_position, game_type in enumerate([
            StatsPlayType.SOLO,
            StatsPlayType.DUO,
            StatsPlayType.SQUAD
        ]):
            game_data = stats.get(game_type)

            deaths = game_data.deaths if game_data.deaths > 0 else 1
            played = game_data.played if game_data.played > 0 else 1

            top10s = game_data.top10s - game_data.wins
            losses = game_data.losses - top10s

            wins_ratio = game_data.wins / played
            top10s_ratio = (game_data.top10s - game_data.wins) / played
            # losses_ratio = (game_data.losses - (game_data.top10s - game_data.wins)) / played

            wins_range = int(wins_ratio * 208)
            top10s_range = int(top10s_ratio * 208)
            # losses_range = int(losses_ratio * 208)
            draw_canvas.rectangle(
                (
                    10 + ((canvas.width - 20) / 6) * (2 * category_position + 1) - 104,
                    158,
                    10 + ((canvas.width - 20) / 6) * (2 * category_position + 1) - 104 + wins_range,
                    178
                ), fill="#22ae22"
            )
            draw_canvas.rectangle(
                (
                    10 + ((canvas.width - 20) / 6) * (2 * category_position + 1) - 104 + wins_range,
                    158,
                    10 + ((canvas.width - 20) / 6) * (2 * category_position + 1) - 104 + wins_range + top10s_range,
                    178
                ), fill="#f1ca09"
            )
            right_align = 10 + ((canvas.width - 20) / 6) * (2 * category_position + 1) + 104
            draw_canvas.rectangle(
                (
                    10 + ((canvas.width - 20) / 6) * (2 * category_position + 1) - 104 + wins_range + top10s_range,
                    158,
                    right_align,
                    178
                ), fill="#af2222"
            )

            # W/T/L
            wtl_text = "{}W {}T {}L".format(game_data.wins, top10s, losses)
            wtl_text_w, wtl_text_h = draw_canvas.textsize(wtl_text, font=self.sub_description_font)
            draw_canvas.text((right_align - wtl_text_w, 182), wtl_text, font=self.sub_description_font)

            # Played Time
            play_time = str()
            play_time_hours = game_data.playtime // 3600
            play_time_minutes = game_data.playtime % 3600 // 60
            play_time_seconds = game_data.playtime % 3600 % 60
            if play_time_hours != 0:
                play_time += "{}시간".format(int(play_time_hours))
            if play_time_hours != 0 or play_time_minutes != 0:
                play_time += "{}분".format(int(play_time_minutes))
            play_time += "{}초".format(int(play_time_seconds))

            play_time_text_w, _ = draw_canvas.textsize(play_time, font=self.play_time_font)
            draw_canvas.text(
                (right_align - play_time_text_w, 186 + wtl_text_h),
                play_time,
                font=self.play_time_font,
                fill="#d4ddf4"
            )

            deployment = [
                {
                    "kda": "{}점".format(round((game_data.kills + game_data.assists) / deaths, 2)),
                    "wins_ratio": "{}%".format(round(wins_ratio * 100, 1))
                }, {
                    "average_deals": str(round(game_data.deals / played, 1)),
                    "max_kills": "{}회".format(game_data.max_kills)
                }
            ]
            # KDA / Win ratio / Average Deals / Max Kill
            for sub_title_position, item in enumerate(deployment):
                height = [230, 291]
                for index, (key, value) in enumerate(item.items()):
                    sub_title1_w, sub_title1_h = draw_canvas.textsize(
                        comment('normal_stats', key, self.language),
                        font=self.sub_title_font
                    )
                    draw_canvas.text(
                        (
                            20 * (category_position + 1)
                            + (canvas.width - 80) / 12 * (1 + 2 * (category_position * 2 + sub_title_position))
                            - sub_title1_w / 2,
                            height[index]
                        ),
                        text=comment('normal_stats', key, self.language),
                        fill="#f1ca09",
                        font=self.sub_title_font
                    )
                    sub_description1_w, sub_description1_h = draw_canvas.textsize(value, font=self.sub_title_font)
                    draw_canvas.text(
                        (
                            20 * (category_position + 1)
                            + (canvas.width - 80) / 12 * (1 + 2 * (category_position * 2 + sub_title_position))
                            - sub_description1_w / 2,
                            height[index] + 30
                        ),
                        text=value,
                        fill="#ffffff",
                        font=self.sub_title_font
                    )

        canvas.show()
        return
