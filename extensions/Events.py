import discord
from discord.ext import commands
from discord import app_commands

from structures.User import User

from functions.database import database

from functions.blacklists import is_person_blacklisted
from functions.blacklists import is_channel_blacklisted

from config import DATABASE_FILE_PATH

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        else:
            user = User(message.author.id, message.author.name)
            
            if not (is_channel_blacklisted(message.channel.id) or is_person_blacklisted(message.author.id)):
                db = database(DATABASE_FILE_PATH)
                db.add_user(user=user)
                db.add_message(message.author.id)

                print(f"🟢 | 1 Message added to {message.author.name}")
            

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is not None:
            await member.send(f"Welcome to {after.channel.name}!")

async def setup(bot):
    await bot.add_cog(Events(bot=bot))