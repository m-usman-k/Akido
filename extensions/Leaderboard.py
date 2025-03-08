import discord, json
from discord.ext import commands
from discord import app_commands

from structures.User import User
from functions.database import database

from config import EMBED_COLOR_CODE
from config import DATABASE_FILE_PATH
from config import DEFAULTS_JSON_FILE_PATH




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

    @app_commands.command(name="set-max-voicetime", description="Set the max voicetime for which the user will get points at one go.")
    async def set_max_voicetime(self, interaction: discord.Interaction, max_time: int):
        
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)

        data["max_voice_points"] = max_time

        with open(DEFAULTS_JSON_FILE_PATH, "w") as file:
            json.dump(data, file, indent=4)

        embed = discord.Embed(
            title="Max Voicetime Set",
            description=f"Max Voicetime has been set to {max_time} minutes.",
            color=EMBED_COLOR_CODE
        )

        await interaction.response.send_message(embed=embed)

    


async def setup(bot):
    await bot.add_cog(Leaderboard(bot=bot))