import discord
from directory import directory


async def forbidden_manage(ctx):
    embed_warning = discord.Embed(
        title="\U000026A0경고!",
        description="권한설정이 잘못되었습니다! 메세지 관리를 활성해 주세요.\n메세지 관리 권한이 활성화 되지 않을 경우 디스코드봇이 정상적으로 작동하지 않습니다.",
        color=0xffd619)
    file_warning = discord.File(f"{directory}/asset/manage_message.png")
    embed_warning.set_image(url="attachment://manage_message.png")
    embed_warning.add_field(
        name="Q: 왜 `메세지 관리`가 필요한가요?",
        value="A: 선택형을 해야하는 메세지(동적 메세지)는 메세지 꼬임 방지를 위하여, 모든 반응을 삭제해야하도록 만들었습니다. 그러나 모든 반응을 삭제하기 위해서는 `메세지 관리` 권한이 "
              "필요합니다.",
        inline=True)
    await ctx.send(embed=embed_warning, file=file_warning)
    return
