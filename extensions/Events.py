import datetime
import discord, asyncio, json
from discord.ext import commands
from discord import app_commands

from structures.User import User

from functions.database import database

from functions.blacklists import is_person_blacklisted
from functions.blacklists import is_channel_blacklisted

from config import EMBED_COLOR_CODE
from config import DATABASE_FILE_PATH
from config import DEFAULTS_JSON_FILE_PATH

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_users = {}

    async def grant_voicetime(self, member: discord.Member):

        """Grant XP every minute while in VC, stopping at 120 minutes."""
        while member.id in self.voice_users:
            await asyncio.sleep(60)  # Wait for 1 minute

            if member.voice and member.voice.channel:  # Check if still in VC
                user_data = self.voice_users[member.id]

                data = {}
                with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
                    data = json.load(file)

                max_voice_points = data["max_voice_points"]
                

                if user_data["total_minutes"] < max_voice_points:
                    user_data["total_minutes"] += 1
                    self.voice_users[member.id] = user_data
                    
                    if not (is_channel_blacklisted(member.voice.channel.id) or is_person_blacklisted(member.id)):
                        db = database(DATABASE_FILE_PATH)
                        db.add_user(User(member.id, member.name))
                        db.add_voicetime(member.id)

                        print(f"🟢 | 1 Minute added to {member.name}")

                else:
                    print(f"{member.display_name} has reached the 120-minute limit.")
                    del self.voice_users[member.id]
                    break
            else:
                del self.voice_users[member.id]
                break


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel and not before.channel:  # User joined a VC
            if member.id not in self.voice_users:
                self.voice_users[member.id] = {
                    "start_time": datetime.datetime.utcnow(),
                    "total_minutes": 0
                }
            await self.grant_voicetime(member)
        
        elif before.channel and not after.channel:  # User left a VC
            if member.id in self.voice_users:
                del self.voice_users[member.id]  # Remove user from tracking


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
            

async def setup(bot):
    await bot.add_cog(Events(bot=bot))