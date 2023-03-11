import os
import io

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

        self.player_name_font = ImageFont.truetype(
            os.path.join(directory, "assets", "fonts", "NotoSansKR-Black.otf"),
            size=36
        )

        self.normal_sub_title_font = ImageFont.truetype(
            os.path.join(directory, "assets", "fonts", "TmoneyRoundWindExtraBold.otf"),
            size=16
        )
        self.normal_sub_description_font = ImageFont.truetype(
            os.path.join(directory, "assets", "fonts", "TmoneyRoundWindExtraBold.otf"),
            size=20
        )

        self.ranked_sub_title_font = ImageFont.truetype(
            os.path.join(directory, "assets", "fonts", "TmoneyRoundWindExtraBold.otf"),
            size=20
        )
        self.ranked_sub_description_font = ImageFont.truetype(
            os.path.join(directory, "assets", "fonts", "TmoneyRoundWindExtraBold.otf"),
            size=30
        )
        self.ranked_sub_description2_font = ImageFont.truetype(
            os.path.join(directory, "assets", "fonts", "TmoneyRoundWindExtraBold.otf"),
            size=16
        )

        self.play_time_font = ImageFont.truetype(
            os.path.join(directory, "assets", "fonts", "TmoneyRoundWindExtraBold.otf"),
            size=16
        )

        self.tier_font = ImageFont.truetype(
            os.path.join(directory, "assets", "fonts", "TmoneyRoundWindExtraBold.otf"),
            size=30
        )
        self.point_font = ImageFont.truetype(
            os.path.join(directory, "assets", "fonts", "TmoneyRoundWindRegular.otf"),
            size=16
        )
        self.player = player_info
        self.language = language

    def base_canvas(
            self,
            layout: Image,
            stats: dict[StatsPlayType, database.NormalStats | database.RankedStats | None],
            canvas_size: tuple[int, int],
            update_location: tuple[int, int]
    ):
        canvas = Image.new('RGBA', canvas_size)

        canvas.paste(self.background_canvas, (0, 0))
        canvas.paste(layout, (0, 0), mask=layout.split()[3])

        draw_canvas = ImageDraw.Draw(canvas, "RGBA")

        # Player Title
        _, player_name_text_h = draw_canvas.textsize(self.player.name, font=self.player_name_font)
        draw_canvas.text(
            (22, (80 - player_name_text_h) / 2),
            self.player.name,
            font=self.player_name_font,
            fill="#f1ca09"
        )

        # Update Date Text
        temp_game_data = stats.get(StatsPlayType.SQUAD)
        update_data = temp_game_data.update_time.strftime("%Y년 %m월 %d일 %H:%M")
        draw_canvas.text(
            update_location, "최근 업데이트: {}".format(update_data),
            font=self.play_time_font,
            fill="#d4ddf4"
        )
        return canvas, draw_canvas

    def normal_stats(self, stats: dict[StatsPlayType, database.NormalStats | None]) -> io.BytesIO:
        layout_canvas = Image.open(
            fp=os.path.join(directory, "assets", "layout", "normal_layout.png")
        )
        self.background_canvas = self.background_canvas.resize((768, 433))
        canvas, draw_canvas = self.base_canvas(layout_canvas, stats, (768, 433), (30, 383))

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
            wtl_text_w, wtl_text_h = draw_canvas.textsize(wtl_text, font=self.normal_sub_description_font)
            draw_canvas.text((right_align - wtl_text_w, 182), wtl_text, font=self.normal_sub_description_font)

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
                        font=self.normal_sub_title_font
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
                        font=self.normal_sub_title_font
                    )
                    sub_description1_w, sub_description1_h = draw_canvas.textsize(
                        value, font=self.normal_sub_description_font
                    )
                    draw_canvas.text(
                        (
                            20 * (category_position + 1)
                            + (canvas.width - 80) / 12 * (1 + 2 * (category_position * 2 + sub_title_position))
                            - sub_description1_w / 2,
                            height[index] + 30
                        ),
                        text=value,
                        fill="#ffffff",
                        font=self.normal_sub_description_font
                    )

        buffer = io.BytesIO()
        canvas.save(buffer, format='png')
        buffer.seek(0)
        return buffer

    @staticmethod
    def _get_rank_file(tier: str | None, sub_tier: str | None):
        if tier is None:
            return "Unranked.png"
        elif tier == "Master":
            return f"{tier}.png"
        return f"{tier}-{sub_tier}.png"

    @staticmethod
    def _rank(tier: str | None, sub_tier: str | None):
        if tier is None:
            return "Unranked"
        elif sub_tier is not None:
            return f"{tier} {sub_tier}"
        return tier

    def ranked_stats(self, stats: dict[StatsPlayType, database.RankedStats]) -> io.BytesIO:
        layout_canvas = Image.open(
            fp=os.path.join(directory, "assets", "layout", "ranked_layout.png")
        )
        self.background_canvas = self.background_canvas.resize((768, 433))
        canvas, draw_canvas = self.base_canvas(layout_canvas, stats, (768, 384), (20, 343))

        game_data = stats[StatsPlayType.SQUAD]

        deaths = game_data.deaths if game_data.deaths > 0 else 1
        played = game_data.played if game_data.played > 0 else 1

        def text_deployment(
                deployment: dict[str, str],
                section_box: tuple[int, int, int, int],
                title_font: ImageFont.FreeTypeFont,
                description_font: ImageFont.FreeTypeFont,
                title_color: str | None = None,
                description_color: str | None = None,
                title_font_padding: int = 15
        ):
            section_box_min_w, section_box_min_h, section_box_max_w, section_box_max_h = section_box
            section_box_span_w = section_box_max_w - section_box_min_w
            section_box_span_h = section_box_max_h - section_box_min_h
            for index, (key, value) in enumerate(deployment.items()):
                title_text_w, title_text_h = draw_canvas.textsize(
                    comment('ranked_stats', key, self.language), font=title_font
                )
                description_text_w, description_text_h = draw_canvas.textsize(value, font=description_font)
                draw_canvas.text(
                    (
                        section_box_min_w + section_box_span_w // 8 * (2 * index + 1) - title_text_w // 2,
                        section_box_min_h + title_font_padding
                    ), comment('ranked_stats', key, self.language), font=title_font, fill=title_color
                )
                draw_canvas.text(
                    (
                        section_box_min_w + section_box_span_w // 8 * (2 * index + 1) - description_text_w // 2,
                        section_box_min_h + title_font_padding + (section_box_span_h - title_font_padding) // 2
                    ), value, font=description_font, fill=description_color
                )
                pass
            return

        # section1 (KDA/Win Ratio/Average Deals/Average Rank)
        section_deployment = {
            "kda": "{}점".format(round(game_data.kda_point, 2)),
            "wins_ratio": "{}%".format(round(game_data.win_point * 100, 1)),
            "average_deals": "{}".format(round(game_data.deals / played, 1)),
            "average_rank": "{}위".format(round(game_data.average_rank, 1))
        }
        text_deployment(
            section_deployment,
            (10, 100, 531, 260),
            self.ranked_sub_title_font,
            self.ranked_sub_description_font,
            "#f1ca09",
            title_font_padding=10
        )

        # section2 (Best/WTL/DBNOs/KD)
        section_deployment = {
            "best_rank": "{}".format(game_data.best_tier),
            "wtl": "{}승 {}탑 {}패".format(game_data.wins, game_data.top10s, game_data.deaths),
            "dbnos": "{}".format(game_data.dbnos),
            "kd": "{}점".format(round(game_data.kills / deaths, 1))
        }
        text_deployment(
            section_deployment,
            (10, 270, 531, 340),
            self.ranked_sub_description2_font,
            self.ranked_sub_description2_font,
            "#f1ca09", "#ccd4eb",
            title_font_padding=5
        )

        # section3
        rank_file_name = self._get_rank_file(game_data.current_tier, game_data.current_sub_tier)
        rank_image = Image.open(fp=os.path.join(directory, "assets", "insignias", rank_file_name))
        tier_text_w, tier_text_h = draw_canvas.textsize(
            self._rank(game_data.current_tier, game_data.current_sub_tier),
            font=self.tier_font
        )
        point_text_w, point_text_h = draw_canvas.textsize("({}점)".format(game_data.current_point), font=self.point_font)

        rank_image = rank_image.resize(
            (int(rank_image.width / rank_image.height * 100), 100)
        )
        rank_image = rank_image.convert("RGBA")
        section3_height = 97 + (274 - (rank_image.height + tier_text_h + point_text_h + 11)) // 2

        canvas.paste(
            rank_image,
            (
                541 + (217 - rank_image.width) // 2,
                section3_height
            ),
            rank_image
        )
        draw_canvas.text(
            (541 + (217 - tier_text_w) // 2, section3_height + rank_image.height + 4),
            self._rank(game_data.current_tier, game_data.current_sub_tier),
            font=self.tier_font
        )
        draw_canvas.text(
            (541 + (217 - point_text_w) // 2, section3_height + rank_image.height + tier_text_h + 11),
            "{}점".format(game_data.current_point),
            font=self.point_font, fill="#d4ddf4"
        )

        buffer = io.BytesIO()
        canvas.save(buffer, format='png')
        buffer.seek(0)
        return buffer
