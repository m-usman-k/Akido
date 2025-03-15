import datetime
import discord, asyncio, json
from discord.ext import commands
from discord import app_commands

from structures.User import User

from functions.database import database

from functions.defaults import is_tracking
from functions.defaults import get_tracking_start_date
from functions.permissions import check_permission

from functions.jail import get_jail_role
from functions.jail import is_person_jailed

from functions.blacklists import is_person_blacklisted
from functions.blacklists import is_channel_blacklisted

from config import EMBED_COLOR_CODE
from config import DATABASE_FILE_PATH
from config import DEFAULTS_JSON_FILE_PATH

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_users = {}

    async def is_person_jailed(self, user_id: int):
        db = database(DATABASE_FILE_PATH)
        return db.is_person_jailed(user_id)
    
    async def get_jail_role(self):
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)

        return data["jail_role"]
    
    async def is_alone_voice_enabled(self):
        """Check if alone voice tracking is enabled"""
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)
        
        return data.get("alone_voice_enabled", True)  # Default to True if not set

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
                
                # Check if user is alone in voice channel and if alone voice is disabled
                alone_in_voice = len(member.voice.channel.members) == 1
                alone_voice_enabled = await self.is_alone_voice_enabled()
                
                if alone_in_voice and not alone_voice_enabled:
                    # Skip giving points if alone and alone voice is disabled
                    print(f"🔴 | {member.name} is alone in voice channel and alone voice tracking is disabled")
                    user_data["total_minutes"] += 1
                    self.voice_users[member.id] = user_data
                    continue

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

    @app_commands.command(name="toggle-alone-voice", description="Toggle whether users alone in voice channels should receive points")
    async def toggle_alone_voice(self, interaction: discord.Interaction):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "toggle-alone-voice"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
        
        # Load current settings
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)
        
        # Toggle the setting (default to True if not set)
        current_setting = data.get("alone_voice_enabled", True)
        data["alone_voice_enabled"] = not current_setting
        
        # Save the updated settings
        with open(DEFAULTS_JSON_FILE_PATH, "w") as file:
            json.dump(data, file, indent=4)
        
        # Create response embed
        embed = discord.Embed(
            title="Alone Voice Setting",
            description=f"Alone voice tracking has been {'enabled' if data['alone_voice_enabled'] else 'disabled'}.",
            color=EMBED_COLOR_CODE
        )
        
        embed.add_field(
            name="What this means",
            value="When enabled, users who are alone in voice channels will receive points.\nWhen disabled, users must have at least one other person in the voice channel to receive points.",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if await is_tracking():
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
        if message.author != self.bot.user and await is_tracking():
            user = User(message.author.id, message.author.name)
            
            if not (is_channel_blacklisted(message.channel.id) or is_person_blacklisted(message.author.id)):
                db = database(DATABASE_FILE_PATH)
                db.add_user(user=user)
                db.add_message(message.author.id)

                print(f"🟢 | 1 Message added to {message.author.name}")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # Check if the user is jailed
        if await is_person_jailed(user_id=member.id):
            role_id = await get_jail_role()
            if role_id:
                guild = member.guild
                role = guild.get_role(role_id)
                if role:
                    await member.add_roles(role)
                    print(f"Reassigned jail role to {member.name} ({member.id})")
                
                    # Send notification to jail logs
                    # Get the jail logs channel
                    with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
                        data = json.load(file)
                    log_channel_id = data.get("jail_logs_channel")
                    if log_channel_id:
                        log_channel = guild.get_channel(log_channel_id)
                        if log_channel:
                            embed = discord.Embed(
                                title="⚠️ Jailed User Rejoined",
                                description=f"{member.mention} has rejoined the server while jailed.",
                                color=discord.Color.gold()  # Gold color for the embed
                            )
                            embed.add_field(name="User ID", value=member.id, inline=False)
                            embed.add_field(name="Action Taken", value="Jail role has been automatically reapplied", inline=False)
                            embed.timestamp = datetime.datetime.utcnow()
                            await log_channel.send(embed=embed)
                else:
                    print(f"Jail role with ID {role_id} not found in {guild.name}.")
            else:
                print("No jail role ID found.")

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Removes any additional roles from jailed users but allows the jail role to be added."""
        if await is_person_jailed(after.id):
            jail_role_id = await get_jail_role()
            jail_role = after.guild.get_role(jail_role_id)

            if not jail_role:
                return  # If the jail role is not found, do nothing

            # Find roles that were added (excluding the jail role)
            added_roles = [role for role in after.roles if role not in before.roles and role.id != jail_role_id]

            # Allow the jail role to be added
            if jail_role not in before.roles and jail_role in after.roles:
                added_roles.remove(jail_role) if jail_role in added_roles else None

            if added_roles:
                await after.remove_roles(*added_roles)
                print(f"Removed unauthorized roles from jailed user {after.name} ({after.id})")

async def setup(bot):
    await bot.add_cog(Events(bot=bot))