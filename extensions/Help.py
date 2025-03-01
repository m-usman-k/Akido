import discord
from discord.ext import commands
from discord import app_commands



class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot


    # Commands:
    @app_commands.command(name="help", description="A command to display all the commands available.")
    async def help(self, interaction: discord.Interaction):
        await interaction.response.send_message("Help command")


async def setup(bot):
    await bot.add_cog(Help(bot=bot))