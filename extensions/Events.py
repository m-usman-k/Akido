import discord
from discord.ext import commands
from discord import app_commands

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.content.startswith("hello"):
            await message.channel.send("Hello!")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is not None:
            await member.send(f"Welcome to {after.channel.name}!")

async def setup(bot):
    await bot.add_cog(Events(bot=bot))