import discord 
from discord.ext import commands


class Permissions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot




async def setup(bot):
    await bot.add_cog(Permissions(bot=bot))