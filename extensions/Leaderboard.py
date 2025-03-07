import discord
from discord.ext import commands
from discord import app_commands

from structures.User import User
from functions.database import database

from config import EMBED_COLOR_CODE
from config import DATABASE_FILE_PATH




class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="user-stats", description="Check your points")
    async def user_stats(self, interaction: discord.Interaction, user: discord
    .User = None):
        if user is None:
            user = interaction.user

        db = database(DATABASE_FILE_PATH)
        db.add_user(user=User(user.id, user.name))
        selected_user: User = db.get_user(user.id)

        embed = discord.Embed(
            title="Your Statistics",
            description=f"",
            color=EMBED_COLOR_CODE
        )

        embed.add_field(name="Messages", value=f"{selected_user.messages} Messages", inline=False)
        embed.add_field(name="Voice Time", value=f"{round(selected_user.voicetime/60, 2)} Hours", inline=False)

        await interaction.response.send_message(embed=embed)

    


async def setup(bot):
    await bot.add_cog(Leaderboard(bot=bot))