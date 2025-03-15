import discord, json
from discord.ext import commands
from discord import app_commands
from datetime import datetime

from structures.User import User

from functions.database import database
from functions.defaults import is_tracking
from functions.defaults import get_days_passed
from functions.defaults import stats_roles_set
from functions.defaults import get_tracking_start_date
from functions.defaults import reset_tracking_start_date
from functions.permissions import check_permission

from functions.blacklists import is_person_eligible

from config import GUILD_ID
from config import EMBED_COLOR_CODE
from config import DATABASE_FILE_PATH
from config import DEFAULTS_JSON_FILE_PATH
from config import BLACKLISTS_JSON_FILE_PATH




class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_log_channel(self, guild: discord.Guild):
        """Fetch the log channel from the stored settings."""
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)
        channel_id = data.get("announcement_logs_channel")
        return guild.get_channel(channel_id) if channel_id else None

    async def log_role_change(self, guild: discord.Guild, user: discord.Member, role: discord.Role, action: str, days_passed=None):
        """Send logs when roles are added or removed."""
        log_channel = await self.get_log_channel(guild)
        if log_channel:
            embed = discord.Embed(
                title="Role Change Log",
                description=f"**Action:** {action}" + (f" after {days_passed} days" if days_passed else ""),
                color=EMBED_COLOR_CODE if action == "Added" else EMBED_COLOR_CODE
            )
            embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=False)
            embed.add_field(name="Role", value=f"{role.mention} ({role.id})", inline=False)
            
            if days_passed is not None:
                embed.add_field(name="Days Since Announcement", value=f"{days_passed} days", inline=False)
            
            embed.timestamp = datetime.now()

            await log_channel.send(embed=embed)

    async def log_bulk_role_changes(self, guild: discord.Guild, role_changes, days_passed):
        """Log multiple role changes in a single embed."""
        log_channel = await self.get_log_channel(guild)
        if log_channel and role_changes:
            embed = discord.Embed(
                title="Leaderboard Role Changes",
                description=f"Role changes after {days_passed} days of tracking.",
                color=EMBED_COLOR_CODE
            )
            
            # Add removed roles section if any
            if role_changes["removed"]:
                removed_text = ""
                for user_id, role_id in role_changes["removed"]:
                    user = guild.get_member(user_id)
                    role = guild.get_role(role_id)
                    if user and role:
                        removed_text += f"• {role.mention} removed from {user.mention}\n"
                
                if removed_text:
                    embed.add_field(name=f"Removed", value=removed_text, inline=False)
            
            # Add added roles section if any
            if role_changes["added"]:
                added_text = ""
                for user_id, role_id in role_changes["added"]:
                    user = guild.get_member(user_id)
                    role = guild.get_role(role_id)
                    if user and role:
                        added_text += f"• {role.mention} added to {user.mention}\n"
                
                if added_text:
                    embed.add_field(name=f"Added", value=added_text, inline=False)
            
            embed.timestamp = datetime.now()
            
            await log_channel.send(embed=embed)

    async def log_tracking_action(self, interaction: discord.Interaction, action: str, additional_info: str = None):
        """Log tracking-related actions (start, stop, reset)."""
        guild = interaction.guild
        log_channel = await self.get_log_channel(guild)
        
        if log_channel:
            title = ""
            description = ""
            
            if action == "Started" or action == "Stopped" or action == "Reset":
                title = f"Tracking {action}"
                description = f"Tracking {action} by {interaction.user.mention}"
            elif action == "Announced and Reset":
                title = "Announcement"
                description = "Announcement has been sent.\nLeaderboard has been reset."

            embed = discord.Embed(
                title=title,
                description=description,
                color=EMBED_COLOR_CODE
            )
            
            if additional_info:
                embed.add_field(name="Additional Information", value=additional_info, inline=False)
                
            embed.timestamp = datetime.now()
            
            await log_channel.send(embed=embed)

    async def generate_announcement_preview(self, guild: discord.Guild):
        """Generate a preview of what the announcement would look like."""
        # Get Database
        db = database(DATABASE_FILE_PATH)
        message_leaderboard = db.get_message_leaderboard()  # List of top message users
        voice_leaderboard = db.get_voicetime_leaderboard()  # List of top voice users

        # Load Config
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)

        top_stats_role = guild.get_role(data["top_stats_role"])
        sub_stats_role = guild.get_role(data.get("sub_stats_role", 0))

        if not top_stats_role:
            return None, "Top stats role not found."

        # Find the top 3 users (regardless of eligibility)
        top_3_messages = message_leaderboard[:3]
        top_3_voice = voice_leaderboard[:3]

        # Find the top 3 **eligible** users
        eligible_message_users = [user for user in message_leaderboard if is_person_eligible(user.userid)]
        eligible_voice_users = [user for user in voice_leaderboard if is_person_eligible(user.userid)]

        # Format Leaderboard Message
        async def format_leaderboard_preview(users, stat_format):
            leaderboard_text = ""
            for index, user in enumerate(users[:3]):
                try:
                    member = await guild.fetch_member(user.userid)
                    mention = member.mention if member else f"UserID: {user.userid}"
                    leaderboard_text += f"\n:{['first', 'second', 'third'][index]}_place: {mention} `{stat_format(user)}`"
                except discord.NotFound:
                    leaderboard_text += f"\n:{['first', 'second', 'third'][index]}_place: UserID: {user.userid} `{stat_format(user)}`"
                except Exception as e:
                    leaderboard_text += f"\n:{['first', 'second', 'third'][index]}_place: Error fetching user: {str(e)}"

            return leaderboard_text

        days_passed = await get_days_passed()
        
        message_leaderboard_text = await format_leaderboard_preview(top_3_messages, lambda u: u.messages)
        voice_leaderboard_text = await format_leaderboard_preview(top_3_voice, lambda u: f"{u.voicetime/60:.2f}h")

        final_message = f"""**TOP Aktivität der letzten {days_passed} Tage** :trophy:

__**Chat-Nachrichten:**__\n{message_leaderboard_text}

__**Voice-Channel:**__\n{voice_leaderboard_text}

__**Eure Vorteile als Poweruser:**__
✘ Eine besondere Rolle
✘ Die Möglichkeit euren Namen zu ändern
✘ Benutzung von GIFs

**Vielen Dank für eure Aktivität!**
**Ihr wollt auch die {top_stats_role.mention} Rolle bekommen? Dann werdet jetzt aktiv im Chat und Voice!**
-# Teamler sind vom Erhalt der Poweruser Rolle ausgeschlossen!"""

        # Create summary of eligible users who would get roles
        summary = {
            "days_passed": days_passed,
            "top_message_users": [{"name": user.username, "messages": user.messages} for user in eligible_message_users[:3]],
            "top_voice_users": [{"name": user.username, "hours": round(user.voicetime/60, 2)} for user in eligible_voice_users[:3]],
            "message": final_message
        }

        return summary, None

    @app_commands.command(name="set-announcement-logs", description="Set channel for recording logs of announcements")
    async def set_announcement_logs(self, interaction: discord.Interaction, channel: discord.TextChannel):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "set-announcement-logs"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
        
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            all_data = json.load(file)

        all_data["announcement_logs_channel"] = channel.id

        with open(DEFAULTS_JSON_FILE_PATH, "w") as file:
            json.dump(all_data, file, indent=4)

        embed = discord.Embed(
            title="Announcement Logs",
            description=f"Channel set to {channel.mention}",
            color=EMBED_COLOR_CODE
        )

        return await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="show-test-announcement", description="Show a preview of what the announcement would look like if done today")
    async def show_test_announcement(self, interaction: discord.Interaction):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "show-test-announcement"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        guild = interaction.guild
        summary, error = await self.generate_announcement_preview(guild)
        
        if error:
            embed = discord.Embed(
                title="Error Generating Preview",
                description=error,
                color=discord.Color.red()
            )
            return await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Load Config for roles
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)
        
        top_stats_role = guild.get_role(data["top_stats_role"])
        sub_stats_role = guild.get_role(data.get("sub_stats_role", 0))
        
        if not top_stats_role:
            embed = discord.Embed(
                title="Error Generating Preview",
                description="Top stats role not found.",
                color=discord.Color.red()
            )
            return await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Get Database
        db = database(DATABASE_FILE_PATH)
        message_leaderboard = db.get_message_leaderboard()
        voice_leaderboard = db.get_voicetime_leaderboard()
        
        # Find eligible users
        eligible_message_users = [user for user in message_leaderboard if is_person_eligible(user.userid)]
        eligible_voice_users = [user for user in voice_leaderboard if is_person_eligible(user.userid)]
        
        # Simulate role assignments
        role_assignments = {
            "top_role": [],  # Will store usernames who would get top role
            "sub_role": []   # Will store usernames who would get sub role
        }
        
        # Simulate assigning top stats role
        awarded_users = set()
        
        if eligible_message_users:
            role_assignments["top_role"].append(eligible_message_users[0].username)
            awarded_users.add(eligible_message_users[0].userid)
        
        if eligible_voice_users and eligible_voice_users[0].userid not in awarded_users:
            role_assignments["top_role"].append(eligible_voice_users[0].username)
            awarded_users.add(eligible_voice_users[0].userid)
        
        # Simulate assigning sub stats role if it exists
        if sub_stats_role:
            for eligible_user in (eligible_message_users[1:3] + eligible_voice_users[1:3]):
                if eligible_user.userid not in awarded_users:
                    role_assignments["sub_role"].append(eligible_user.username)
                    awarded_users.add(eligible_user.userid)
        
        # Create preview embed
        embed = discord.Embed(
            title="📢 Announcement Preview",
            description="Here's how the announcement would look if done today:",
            color=EMBED_COLOR_CODE
        )
        
        embed.add_field(
            name="Tracking Period", 
            value=f"{summary['days_passed']} days", 
            inline=False
        )
        
        # Top message users
        msg_users = ""
        for i, user in enumerate(summary['top_message_users']):
            msg_users += f"{i+1}. **{user['name']}**: {user['messages']} messages\n"
        
        embed.add_field(
            name="Top Message Users (Eligible)", 
            value=msg_users if msg_users else "No eligible users found", 
            inline=False
        )
        
        # Top voice users
        voice_users = ""
        for i, user in enumerate(summary['top_voice_users']):
            voice_users += f"{i+1}. **{user['name']}**: {user['hours']} hours\n"
        
        embed.add_field(
            name="Top Voice Users (Eligible)", 
            value=voice_users if voice_users else "No eligible users found", 
            inline=False
        )
        
        # Add role assignment preview
        top_role_users = ", ".join(role_assignments["top_role"]) if role_assignments["top_role"] else "None"
        
        embed.add_field(
            name=f"Users Who Would Receive {top_stats_role.name}",
            value=top_role_users,
            inline=False
        )
        
        if sub_stats_role:
            sub_role_users = ", ".join(role_assignments["sub_role"]) if role_assignments["sub_role"] else "None"
            
            embed.add_field(
                name=f"Users Who Would Receive {sub_stats_role.name}",
                value=sub_role_users,
                inline=False
            )
        
        # Send the preview embed
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Send the actual announcement message as a follow-up
        await interaction.followup.send(
            content="**Preview of the announcement message:**\n\n" + summary['message'],
            allowed_mentions=discord.AllowedMentions.none(),
            ephemeral=True  # Ensure this is ephemeral
        )
            
    @app_commands.command(name="reset-tracking", description="Reset the tracking data")
    async def reset_tracking(self, interaction: discord.Interaction):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "reset-tracking"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
        
        # Create confirmation embed
        confirmation_embed = discord.Embed(
            title="⚠️ Confirm Reset Tracking",
            description="Are you sure you want to reset all tracking data? This action cannot be undone.",
            color=discord.Color.red()
        )
        
        # Create confirmation view
        view = ResetTrackingConfirmationView(
            cog=self,
            interaction=interaction
        )
        
        await interaction.response.send_message(embed=confirmation_embed, view=view, ephemeral=True)
    
    async def execute_reset_tracking(self, interaction: discord.Interaction):
        """Execute the reset tracking action after confirmation"""
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)

        data["tracking_start_date"] = round(interaction.created_at.timestamp())

        with open(DEFAULTS_JSON_FILE_PATH, "w") as file:
            json.dump(data, file, indent=4)

        db = database(DATABASE_FILE_PATH)
        db.reset_all_users()

        # Log the reset action
        await self.log_tracking_action(
            interaction, 
            "Reset", 
            "All user message and voice time data has been reset. A new tracking period has started."
        )

        embed = discord.Embed(
            title="Tracking Reset",
            description="Messages and Voicetime have been reset.",
            color=EMBED_COLOR_CODE
        )

        await interaction.followup.send(embed=embed)
            
    @app_commands.command(name="start-tracking", description="Start tracking messages and voicetime")
    async def start_tracking(self, interaction: discord.Interaction):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "start-tracking"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
            
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)

        data["tracking_start_date"] = round(interaction.created_at.timestamp())

        with open(DEFAULTS_JSON_FILE_PATH, "w") as file:
            json.dump(data, file, indent=4)

        # Log the start tracking action
        await self.log_tracking_action(
            interaction, 
            "Started", 
            "Tracking of messages and voice time has been enabled."
        )

        embed = discord.Embed(
            title="Tracking Started",
            description="Messages and Voicetime are now being tracked.",
            color=EMBED_COLOR_CODE
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="stop-tracking", description="Stop tracking messages and voicetime")
    async def stop_tracking(self, interaction: discord.Interaction):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "stop-tracking"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
            
        # Get the current tracking period before stopping
        tracking_period = None
        if await is_tracking():
            start_date = await get_tracking_start_date()
            tracking_period = round((round(interaction.created_at.timestamp()) - start_date) / 86400, 3)
        
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)

        data["tracking_start_date"] = 0

        with open(DEFAULTS_JSON_FILE_PATH, "w") as file:
            json.dump(data, file, indent=4)

        # Log the stop tracking action
        additional_info = "Tracking of messages and voice time has been disabled."
        if tracking_period:
            additional_info += f"\nTracking was active for {tracking_period} days."
        
        await self.log_tracking_action(
            interaction, 
            "Stopped", 
            additional_info
        )

        embed = discord.Embed(
            title="Tracking Stopped",
            description="Messages and Voicetime are no longer being tracked.",
            color=EMBED_COLOR_CODE
        )

        await interaction.response.send_message(embed=embed)
   
    @app_commands.command(name="user-stats", description="Check your points")
    async def user_stats(self, interaction: discord.Interaction, user: discord.User = None):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "user-stats"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
            
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
        # Check if user has permission to use this command
        if not await check_permission(interaction, "set-max-voicetime"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
        
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

    @app_commands.command(name="leaderboard", description="Check leaderboards for both messages and voicetime")
    async def leaderboard(self, interaction: discord.Interaction):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "leaderboard"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
            
        view = LeaderboardView(self.bot, interaction)
        embed = discord.Embed(title="📊 Choose a Leaderboard", description="Select an option from the dropdown menu below.", color=EMBED_COLOR_CODE)
        return await interaction.response.send_message(embed=embed, view=view)
            
    @app_commands.command(name="announce-winners", description="Announce the winners of the tracking period")
    async def announce_winners(self, interaction: discord.Interaction, announcement_channel: discord.TextChannel):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "announce-winners"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
            
        # Check if top stats role is set
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)
        
        if not data.get("top_stats_role", 0):
            embed = discord.Embed(
                title="Top Stats Role Not Set",
                description="Please set the top stats role before using this command.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed)
        
        # Generate preview first to show with confirmation buttons
        await interaction.response.defer(ephemeral=True)
        summary, error = await self.generate_announcement_preview(interaction.guild)
        
        if error:
            embed = discord.Embed(
                title="Error Generating Preview",
                description=error,
                color=discord.Color.red()
            )
            return await interaction.followup.send(embed=embed)
        
        # Create confirmation embed with details
        confirmation_embed = discord.Embed(
            title="📢 Announcement Confirmation",
            description=f"Are you sure you want to announce the winners in {announcement_channel.mention}?",
            color=EMBED_COLOR_CODE
        )
        
        confirmation_embed.add_field(
            name="Tracking Period", 
            value=f"{summary['days_passed']} days", 
            inline=False
        )
        
        # Top message users
        msg_users = ""
        for i, user in enumerate(summary['top_message_users']):
            msg_users += f"{i+1}. **{user['name']}**: {user['messages']} messages\n"
        
        confirmation_embed.add_field(
            name="Top Message Users (Eligible for Roles)", 
            value=msg_users if msg_users else "No eligible users found", 
            inline=False
        )
        
        # Top voice users
        voice_users = ""
        for i, user in enumerate(summary['top_voice_users']):
            voice_users += f"{i+1}. **{user['name']}**: {user['hours']} hours\n"
        
        confirmation_embed.add_field(
            name="Top Voice Users (Eligible for Roles)", 
            value=voice_users if voice_users else "No eligible users found", 
            inline=False
        )
        
        confirmation_embed.add_field(
            name="Warning", 
            value="This will reset all tracking data and reassign roles!", 
            inline=False
        )
        
        # Send confirmation with buttons
        view = ConfirmationView(
            origional_interaction=interaction, 
            announcement_channel=announcement_channel, 
            bot=self.bot
        )
        
        return await interaction.followup.send(embed=confirmation_embed, view=view)

    @app_commands.command(name="set-sub-stats-role", description="Setup the role which is to be assigned to the remaining two person of message & voice leaderboard")
    async def set_sub_stats_role(self, interaction: discord.Interaction, role: discord.Role):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "set-sub-stats-role"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
            
        data = []
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)

            data["sub_stats_role"] = role.id

        with open(DEFAULTS_JSON_FILE_PATH, "w") as file:
            json.dump(data, file, indent=4)
        
        embed = discord.Embed(
            title="Sub Stats Role Set",
            description=f"Role set to {role.mention}",
            color=EMBED_COLOR_CODE
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="remove-sub-stats-role", description="Remove the sub stats role from the settings")
    async def remove_sub_stats_role(self, interaction: discord.Interaction):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "remove-sub-stats-role"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
        
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)
        
        # Check if sub stats role is set
        if "sub_stats_role" not in data or data.get("sub_stats_role", 0) == 0:
            embed = discord.Embed(
                title="Sub Stats Role Not Set",
                description="There is no sub stats role currently set.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed)
        
        # Get the role for the message
        sub_stats_role = interaction.guild.get_role(data["sub_stats_role"])
        role_mention = sub_stats_role.mention if sub_stats_role else f"Role ID: {data['sub_stats_role']}"
        
        # Remove the sub stats role from the settings
        data.pop("sub_stats_role", None)
        
        with open(DEFAULTS_JSON_FILE_PATH, "w") as file:
            json.dump(data, file, indent=4)
        
        embed = discord.Embed(
            title="Sub Stats Role Removed",
            description=f"The sub stats role ({role_mention}) has been removed from the settings.",
            color=EMBED_COLOR_CODE
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="set-top-stats-role", description="Setup the role which is to be assigned to the top 1 person of message & voice leaderboard")
    async def set_top_stats_role(self, interaction: discord.Interaction, role: discord.Role):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "set-top-stats-role"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
            
        data = []
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)

            data["top_stats_role"] = role.id

        with open(DEFAULTS_JSON_FILE_PATH, "w") as file:
            json.dump(data, file, indent=4)
        
        embed = discord.Embed(
            title="Top Stats Role Set",
            description=f"Role set to {role.mention}",
            color=EMBED_COLOR_CODE
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tracking-status", description="Check if tracking is enabled")
    async def tracking_status(self, interaction: discord.Interaction):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "tracking-status"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
            
        if await is_tracking():

            start_date = await get_tracking_start_date()
            num_days = round((round(interaction.created_at.timestamp()) - start_date) / 86400, 3)

            embed = discord.Embed(
                title="Tracking Status",
                description="Tracking is currently enabled.",
                color=EMBED_COLOR_CODE
            )

            embed.add_field(name="Tracking Period", value=f"{num_days} Days", inline=False)
        else:
            embed = discord.Embed(
                title="Tracking Status",
                description="Tracking is currently disabled.",
                color=EMBED_COLOR_CODE
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="poweruser-settings", description="Display all settings and configurations for poweruser function")
    async def poweruser_settings(self, interaction: discord.Interaction):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "poweruser-settings"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
        
        # Load all settings
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            defaults_data = json.load(file)
        
        with open(BLACKLISTS_JSON_FILE_PATH, "r") as file:
            blacklists_data = json.load(file)
        
        # Get guild for role and channel mentions
        guild = interaction.guild
        
        # Create embed
        embed = discord.Embed(
            title="Settings / Overview",
            color=EMBED_COLOR_CODE
        )
        
        # Blacklisted Roles
        blacklisted_roles = []
        for role_id in blacklists_data["blacklists"]["roles"]:
            role = guild.get_role(role_id)
            if role:
                blacklisted_roles.append(role.mention)
        
        embed.add_field(
            name="Blacklisted Roles",
            value="\n".join(blacklisted_roles) if blacklisted_roles else "None",
            inline=True
        )

        # Blacklisted Users
        blacklisted_users = []
        for role_id in blacklists_data["blacklists"]["users"]:
            role = guild.get_role(role_id)
            if role:
                blacklisted_users.append(role.mention)
        
        embed.add_field(
            name="Blacklisted Users",
            value="\n".join(blacklisted_users) if blacklisted_users else "None",
            inline=True
        )

        # Uneligible Roles
        ineligible_roles = []
        for role_id in blacklists_data["ineligible"]["roles"]:
            role = guild.get_role(role_id)
            if role:
                ineligible_roles.append(role.mention)
        
        embed.add_field(
            name="Ineligible Roles",
            value="\n".join(ineligible_roles) if ineligible_roles else "None",
            inline=True
        )

        # Uneligible Roles
        ineligible_users = []
        for role_id in blacklists_data["ineligible"]["users"]:
            role = guild.get_role(role_id)
            if role:
                ineligible_users.append(role.mention)
        
        embed.add_field(
            name="Ineligible Users",
            value="\n".join(ineligible_users) if ineligible_users else "None",
            inline=True
        )
        
        # Blacklisted Channels
        blacklisted_channels = []
        for channel_id in blacklists_data["blacklists"]["channels"]["text"] + blacklists_data["blacklists"]["channels"]["voice"]:
            channel = guild.get_channel(channel_id)
            if channel:
                blacklisted_channels.append(channel.mention)
        
        embed.add_field(
            name="Blacklisted Channels",
            value="\n".join(blacklisted_channels) if blacklisted_channels else "None",
            inline=True
        )
        
        # Voice Winner Roles
        top_stats_role = guild.get_role(defaults_data.get("top_stats_role", 0))
        sub_stats_role = guild.get_role(defaults_data.get("sub_stats_role", 0))
        
        voice_roles = []
        if top_stats_role:
            voice_roles.append(f"1: {top_stats_role.mention}")
        if sub_stats_role:
            voice_roles.extend([f"2: {sub_stats_role.mention}", f"3: {sub_stats_role.mention}"])
        
        embed.add_field(
            name="Voice Winner Roles",
            value="\n".join(voice_roles) if voice_roles else "Not set",
            inline=True
        )
        
        # Chat Winner Roles (same as voice roles in this case)
        embed.add_field(
            name="Chat Winner Roles",
            value="\n".join(voice_roles) if voice_roles else "Not set",
            inline=True
        )
        
        # Logs Channel
        logs_channel = guild.get_channel(defaults_data.get("announcement_logs_channel", 0))
        embed.add_field(
            name="Logs channel",
            value=logs_channel.mention if logs_channel else "Not set",
            inline=True
        )
        
        # Alone Voice Status
        alone_voice_enabled = defaults_data.get("alone_voice_enabled", True)
        embed.add_field(
            name="Alone Voice",
            value="Enabled" if alone_voice_enabled else "Disabled",
            inline=True
        )
        
        # Max Voice Time
        max_voice = defaults_data.get("max_voice_points", 0)
        embed.add_field(
            name="Max Voice",
            value=f"{max_voice/60:.1f}h" if max_voice else "Not set",
            inline=True
        )
        
        
        # Time Range (total tracking period)
        if await is_tracking():
            start_date = await get_tracking_start_date()
            total_time = round(interaction.created_at.timestamp() - start_date, 2)
            time_range = f"{total_time/3600:.1f}h"
        else:
            time_range = "Tracking disabled"
        
        embed.add_field(
            name="Tracking Time",
            value=time_range,
            inline=True
        )
        
        # Bot Active Status
        embed.add_field(
            name="Bot Active",
            value="Yes" if await is_tracking() else "No",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)

class ResetTrackingConfirmationView(discord.ui.View):
    def __init__(self, cog, interaction):
        super().__init__(timeout=60)
        self.cog = cog
        self.original_interaction = interaction

    @discord.ui.button(label="Confirm Reset", style=discord.ButtonStyle.danger)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await self.cog.execute_reset_tracking(self.original_interaction)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Reset tracking command cancelled.", ephemeral=True)
        self.stop()


class ConfirmationView(discord.ui.View):
    def __init__(self, origional_interaction: discord.Interaction, announcement_channel: discord.TextChannel, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.origional_interaction = origional_interaction
        self.announcement_channel = announcement_channel

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.defer()

        # Load Config
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)

        # Get Database
        db = database(DATABASE_FILE_PATH)
        message_leaderboard = db.get_message_leaderboard()  # List of top message users
        voice_leaderboard = db.get_voicetime_leaderboard()  # List of top voice users

        # Get Guild and Roles
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            print("Guild not found.")
            return

        top_stats_role = guild.get_role(data["top_stats_role"])
        sub_stats_role = guild.get_role(data.get("sub_stats_role", 0))

        if not top_stats_role:
            print("Top stats role not found.")
            return

        # Track role changes for logging
        role_changes = {
            "removed": [],  # Will store tuples of (user_id, role_id)
            "added": []     # Will store tuples of (user_id, role_id)
        }

        # Remove roles from all members before assigning new ones
        for member in guild.members:
            if top_stats_role in member.roles:
                await member.remove_roles(top_stats_role)
                role_changes["removed"].append((member.id, top_stats_role.id))
            if sub_stats_role and sub_stats_role in member.roles:
                await member.remove_roles(sub_stats_role)
                role_changes["removed"].append((member.id, sub_stats_role.id))

        # Find the top 3 users (regardless of eligibility)
        top_3_messages = message_leaderboard[:3]
        top_3_voice = voice_leaderboard[:3]

        # Find the top 3 **eligible** users
        eligible_message_users = [user for user in message_leaderboard if is_person_eligible(user.userid)]
        eligible_voice_users = [user for user in voice_leaderboard if is_person_eligible(user.userid)]

        # Assign Roles:
        awarded_users = set()  # Track users who received a role

        # Assign Top Stats Role to First Eligible User
        if eligible_message_users:
            try:
                first_message_eligible = await guild.fetch_member(eligible_message_users[0].userid)
                if first_message_eligible:
                    await first_message_eligible.add_roles(top_stats_role)
                    role_changes["added"].append((first_message_eligible.id, top_stats_role.id))
                    awarded_users.add(first_message_eligible.id)
                    print(f"Assigned {top_stats_role.name} to {first_message_eligible.display_name}")
            except discord.NotFound:
                print(f"User {eligible_message_users[0].userid} not found in the guild.")

        if eligible_voice_users:
            try:
                first_voice_eligible = await guild.fetch_member(eligible_voice_users[0].userid)
                if first_voice_eligible and first_voice_eligible.id not in awarded_users:
                    await first_voice_eligible.add_roles(top_stats_role)
                    role_changes["added"].append((first_voice_eligible.id, top_stats_role.id))
                    awarded_users.add(first_voice_eligible.id)
                    print(f"Assigned {top_stats_role.name} to {first_voice_eligible.display_name}")
            except discord.NotFound:
                print(f"User {eligible_voice_users[0].userid} not found in the guild.")

        # Assign Sub Stats Role to the Next Two Eligible Users (if sub_stats_role exists)
        if sub_stats_role:
            for eligible_user in (eligible_message_users[1:3] + eligible_voice_users[1:3]):
                try:
                    user = await guild.fetch_member(eligible_user.userid)
                    if user and user.id not in awarded_users:
                        await user.add_roles(sub_stats_role)
                        role_changes["added"].append((user.id, sub_stats_role.id))
                        awarded_users.add(user.id)
                        print(f"Assigned {sub_stats_role.name} to {user.display_name}")
                except discord.NotFound:
                    print(f"User {eligible_user.userid} not found in the guild.")

        # Log all role changes
        days_passed = await get_days_passed()
        await self.bot.get_cog("Leaderboard").log_bulk_role_changes(guild, role_changes, days_passed)

        # Format Leaderboard Message
        async def format_leaderboard(users, stat_format):
            leaderboard_text = ""
            seen_users = set()
            already_mentioned = False
            for index, user in enumerate(users):
                try:
                    member = await guild.fetch_member(user.userid)
                    mention = member.mention if member else f"UserID: {user.userid}"

                    # Only mention the role the first time the user appears
                    role_mention = ""
                    if user.userid in awarded_users and user.userid not in seen_users and not already_mentioned:
                        role_mention = f" {top_stats_role.mention}"
                        already_mentioned = True
                        seen_users.add(user.userid)  # Mark user as seen

                    leaderboard_text += f"\n:{['first', 'second', 'third'][index]}_place: {mention} `{stat_format(user)}`{role_mention}"
                except discord.NotFound:
                    leaderboard_text += f"\n:{['first', 'second', 'third'][index]}_place: UserID: {user.userid} `{stat_format(user)}`"

            return leaderboard_text



        final_message = f"""**TOP Aktivität der letzten {days_passed} Tage** :trophy:

__**Chat-Nachrichten:**__\n{await format_leaderboard(top_3_messages, lambda u: u.messages)}

__**Voice-Channel:**__\n{await format_leaderboard(top_3_voice, lambda u: f"{u.voicetime/60:.2f}h")}

__**Eure Vorteile als Poweruser:**__
✘ Eine besondere Rolle
✘ Die Möglichkeit euren Namen zu ändern
✘ Benutzung von GIFs

**Vielen Dank für eure Aktivität!**
**Ihr wollt auch die {top_stats_role.mention} Rolle bekommen? Dann werdet jetzt aktiv im Chat und Voice!**
-# Teamler sind vom Erhalt der Poweruser Rolle ausgeschlossen!"""

        # Reset Database Tracking
        db.reset_all_users()
        await reset_tracking_start_date()

        # Log the leaderboard announcement and reset
        leaderboard_cog = self.bot.get_cog("Leaderboard")
        if leaderboard_cog:
            await leaderboard_cog.log_tracking_action(
                interaction,
                "Announced and Reset",
                # f"Leaderboard was announced in {self.announcement_channel.mention} after {days_passed} days of tracking.\n"
                # f"Top message user: {eligible_message_users[0].username if eligible_message_users else 'None'}\n"
                # f"Top voice user: {eligible_voice_users[0].username if eligible_voice_users else 'None'}\n"
                # f"Total roles assigned: {len(role_changes['added'])}"
                f"**Executed by**\n{interaction.user.mention}\n\n**Channel**\n{interaction.channel.mention}\n\n**Tracking Time**\n{days_passed} day(s)\n\n**Top Users**\nMessages: {self.bot.get_user(eligible_message_users[0].userid) if eligible_message_users else 'None'}\nVoice: {self.bot.get_user(eligible_voice_users[0].userid) if eligible_voice_users else 'None'}"
            )

        # Send Announcement
        return await self.announcement_channel.send(content=final_message)


    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.defer()
        return await self.origional_interaction.delete_original_response()

class LeaderboardView(discord.ui.View):
    def __init__(self, bot, interaction):
        super().__init__()
        self.add_item(LeaderboardSelect(bot, interaction))


class LeaderboardSelect(discord.ui.Select):
    def __init__(self, bot, interaction):
        self.bot = bot
        self.interaction = interaction
        options = [
            discord.SelectOption(label="Messages", description="Show the top message senders"),
            discord.SelectOption(label="Voice Time", description="Show the top voice channel users"),
        ]
        super().__init__(placeholder="Select a leaderboard...", options=options)

    async def callback(self, interaction: discord.Interaction):
        """Handles the leaderboard selection."""
        if interaction.user.id != self.interaction.user.id:
            return await interaction.response.send_message("You can't interact with this menu!", ephemeral=True)
        
        db_manager = database(DATABASE_FILE_PATH)

        if self.values[0] == "Messages":
            leaderboard_data = db_manager.get_message_leaderboard()
            title = "📩 Message Leaderboard"
            unit = "messages"
        else:
            leaderboard_data = db_manager.get_voicetime_leaderboard()
            title = "🎙️ Voice Time Leaderboard"
            unit = "voicetime"

        embed = discord.Embed(title=title, color=EMBED_COLOR_CODE)

        if unit == "voicetime":
            for rank, user in enumerate(leaderboard_data, start=1):
                embed.add_field(name=f"#{rank} {user.username}", value=f"{round(getattr(user, unit)/60, 2)} hours", inline=False)
        else:
            for rank, user in enumerate(leaderboard_data, start=1):
                embed.add_field(name=f"#{rank} {user.username}", value=f"{getattr(user, unit)} Messages", inline=False)

        await interaction.response.edit_message(embed=embed, view=None)


async def setup(bot):
    await bot.add_cog(Leaderboard(bot=bot))