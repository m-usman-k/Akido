import discord, json
from discord.ext import commands
from discord import app_commands

from structures.User import User

from functions.database import database
from functions.defaults import is_tracking
from functions.defaults import stats_roles_set
from functions.defaults import get_tracking_start_date

from config import EMBED_COLOR_CODE
from config import DATABASE_FILE_PATH
from config import DEFAULTS_JSON_FILE_PATH




class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
            
    @app_commands.command(name="announce-winners", description="Announce the winners of the tracking period")
    async def announce_winners(self, interaction: discord.Interaction, announcement_channel: discord.TextChannel):
        if await stats_roles_set():
            return await interaction.response.send_message(view=ConfirmationView(origional_interaction=interaction, announcement_channel=announcement_channel), ephemeral=True)
        else:
            embed = discord.Embed(
                title="Stats Roles Not Set",
                description="Please check, one of the stats roles are not set.",
                color=EMBED_COLOR_CODE
            )

            return await interaction.response.send_message(embed=embed)

    @app_commands.command(name="set-sub-stats-role", description="Setup the role which is to be assigned to the remaining two person of message & voice leaderboard")
    async def set_sub_stats_role(self, interaction: discord.Interaction, role: discord.Role):
        data = []
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)

            data["sub_stats_role"] = role.id

        with open(DEFAULTS_JSON_FILE_PATH, "w") as file:
            json.dump(data, file, indent=4)
        
        embed = discord.Embed(
            title="Sub Stats Role Set",
            description=f"Role Set To {role.mention}",
            color=EMBED_COLOR_CODE
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="set-top-stats-role", description="Setup the role which is to be assigned to the top 1 person of message & voice leaderboard")
    async def set_top_stats_role(self, interaction: discord.Interaction, role: discord.Role):
        data = []
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)

            data["top_stats_role"] = role.id

        with open(DEFAULTS_JSON_FILE_PATH, "w") as file:
            json.dump(data, file, indent=4)
        
        embed = discord.Embed(
            title="Top Stats Role Set",
            description=f"Role Set To {role.mention}",
            color=EMBED_COLOR_CODE
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tracking-status", description="Check if tracking is enabled")
    async def tracking_status(self, interaction: discord.Interaction):
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

    @app_commands.command(name="reset-tracking", description="Reset the tracking data")
    async def reset_tracking(self, interaction: discord.Interaction):
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)

        data["tracking_start_date"] = round(interaction.created_at.timestamp())

        with open(DEFAULTS_JSON_FILE_PATH, "w") as file:
            json.dump(data, file, indent=4)

        db = database(DATABASE_FILE_PATH)
        db.reset_all_users()

        embed = discord.Embed(
            title="Tracking Reset",
            description="Messages and Voicetime have been reset.",
            color=EMBED_COLOR_CODE
        )

        await interaction.response.send_message(embed=embed)
            
    @app_commands.command(name="start-tracking", description="Start tracking messages and voicetime")
    async def start_tracking(self, interaction: discord.Interaction):
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)

        data["tracking_start_date"] = round(interaction.created_at.timestamp())

        with open(DEFAULTS_JSON_FILE_PATH, "w") as file:
            json.dump(data, file, indent=4)

        embed = discord.Embed(
            title="Tracking Started",
            description="Messages and Voicetime are now being tracked.",
            color=EMBED_COLOR_CODE
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="stop-tracking", description="Stop tracking messages and voicetime")
    async def stop_tracking(self, interaction: discord.Interaction):
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)

        data["tracking_start_date"] = 0

        with open(DEFAULTS_JSON_FILE_PATH, "w") as file:
            json.dump(data, file, indent=4)

        embed = discord.Embed(
            title="Tracking Stopped",
            description="Messages and Voicetime are no longer being tracked.",
            color=EMBED_COLOR_CODE
        )

        await interaction.response.send_message(embed=embed)
   
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

    @app_commands.command(name="leaderboard", description="Check leaderboards for both messages and voicetime")
    async def leaderboard(self, interaction: discord.Interaction):
        view = LeaderboardView(self.bot, interaction)
        embed = discord.Embed(title="📊 Choose a Leaderboard", description="Select an option from the dropdown menu below.", color=EMBED_COLOR_CODE)
        return await interaction.response.send_message(embed=embed, view=view)
    

class ConfirmationView(discord.ui.View):
    def __init__(self, origional_interaction: discord.Interaction, announcement_channel: discord.TextChannel):
        super().__init__(timeout=None)
        self.origional_interaction = origional_interaction
        self.announcement_channel = announcement_channel

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.defer()
        data = []
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)

        db = database(DATABASE_FILE_PATH)
        message_leaderboard = db.get_message_leaderboard()
        voice_leaderboard = db.get_voicetime_leaderboard()

        top_stats_role = interaction.guild.get_role(data["top_stats_role"])
        sub_stats_role = interaction.guild.get_role(data["sub_stats_role"])

        top_3_voice_users = []
        top_3_message_users = []

        final_message = f""""""

        db.reset_all_users()
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