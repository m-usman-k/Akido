import discord, json, asyncio
from discord.ext import commands
from discord import app_commands

from functions.database import database
from structures.User import User
from functions.permissions import check_permission

from config import EMBED_COLOR_CODE
from config import DATABASE_FILE_PATH
from config import DEFAULTS_JSON_FILE_PATH


class Jail(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def is_jail_role_set(self):
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)
        return data.get("jail_role", 0) != 0

    async def get_jail_role(self):
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)
        return data.get("jail_role", 0)

    async def get_log_channel(self, guild: discord.Guild):
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)
        channel_id = data.get("jail_logs_channel")
        return guild.get_channel(channel_id) if channel_id else None

    async def schedule_unjail(self, user: discord.Member, duration: int):
        """Handles automatic unjailing after the specified duration (in minutes)."""
        await asyncio.sleep(duration * 60)  # Convert minutes to seconds

        db = database(DATABASE_FILE_PATH)
        if not db.is_person_jailed(user.id):
            return  # User was manually unjailed before the duration ended

        db.unjail_user(user.id)
        jail_role = user.guild.get_role(await self.get_jail_role())
        await user.remove_roles(jail_role)

        jail_roles = db.get_jail_roles(user.id)
        for role_id in jail_roles:
            role = user.guild.get_role(role_id)
            if role:
                await user.add_roles(role)
                db.remove_jail_role(user.id, role_id)

        log_channel = await self.get_log_channel(user.guild)
        if log_channel:
            embed = discord.Embed(
                title="User Auto-Unjailed",
                description=f"{user.mention} has been unjailed after {duration} minutes.",
                color=discord.Color.green()
            )
            await log_channel.send(embed=embed)
            
        # Send DM to user
        try:
            dm_embed = discord.Embed(
                title="You Have Been Unjailed",
                description=f"You have been automatically unjailed in {user.guild.name} after your jail duration expired.",
                color=discord.Color.green()
            )
            await user.send(embed=dm_embed)
        except:
            # User might have DMs disabled
            pass

    @app_commands.command(name="jail-info", description="Shows the current jail role and log channel settings")
    async def jail_info(self, interaction: discord.Interaction):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "jail-info"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
        
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)
        
        jail_role_id = data.get("jail_role", 0)
        jail_logs_channel_id = data.get("jail_logs_channel")
        
        jail_role = interaction.guild.get_role(jail_role_id) if jail_role_id else None
        jail_logs_channel = interaction.guild.get_channel(jail_logs_channel_id) if jail_logs_channel_id else None
        
        embed = discord.Embed(
            title="Jail System Information",
            description="Current settings for the jail system",
            color=EMBED_COLOR_CODE
        )
        
        embed.add_field(
            name="Jail Role",
            value=f"{jail_role.mention}" if jail_role else "Not set",
            inline=False
        )
        
        embed.add_field(
            name="Jail Logs Channel",
            value=f"{jail_logs_channel.mention}" if jail_logs_channel else "Not set",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="set-jail-role", description="Set the role that will be used for jailed users.")
    async def set_jail_role(self, interaction: discord.Interaction, role: discord.Role):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "set-jail-role"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
        
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)

        data["jail_role"] = role.id

        with open(DEFAULTS_JSON_FILE_PATH, "w") as file:
            json.dump(data, file, indent=4)

        embed = discord.Embed(
            title="Jail Role Set",
            description=f"The jail role has been set to {role.mention}",
            color=EMBED_COLOR_CODE
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="set-jail-logs", description="Set the channel where jail logs will be sent.")
    async def set_jail_logs(self, interaction: discord.Interaction, channel: discord.TextChannel):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "set-jail-logs"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
        
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)

        data["jail_logs_channel"] = channel.id

        with open(DEFAULTS_JSON_FILE_PATH, "w") as file:
            json.dump(data, file, indent=4)

        embed = discord.Embed(
            title="Jail Logs Channel Set",
            description=f"The jail logs channel has been set to {channel.mention}",
            color=EMBED_COLOR_CODE
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="jail", description="Jail a user for an optional duration (days, hours). If no time is given, it's indefinite.")
    async def jail(self, interaction: discord.Interaction, user: discord.Member, reason: str = "-", days: int = 0, hours: int = 0):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "jail"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
        
        # Create confirmation embed
        confirmation_embed = discord.Embed(
            title="Confirm Jail",
            description=f"Are you sure you want to jail {user.mention}?",
            color=discord.Color.red()
        )
        
        duration_text = "Indefinitely"
        total_minutes = (days * 24 * 60) + (hours * 60)
        if total_minutes > 0:
            duration_text = f"{days} days, {hours} hours"
            
        confirmation_embed.add_field(name="User", value=user.mention, inline=False)
        confirmation_embed.add_field(name="Reason", value=reason, inline=False)
        confirmation_embed.add_field(name="Duration", value=duration_text, inline=False)
        
        # Create confirmation view
        view = JailConfirmationView(
            cog=self,
            user=user,
            reason=reason,
            days=days,
            hours=hours,
            interaction=interaction
        )
        
        await interaction.response.send_message(embed=confirmation_embed, view=view, ephemeral=True)

    async def execute_jail(self, interaction: discord.Interaction, user: discord.Member, reason: str, days: int, hours: int):
        """Execute the jail action after confirmation"""
        user_db = User(user.id, user.name)
        db = database(DATABASE_FILE_PATH)
        db.add_user(user=user_db)

        if not await self.is_jail_role_set():
            embed = discord.Embed(
                title="Jail Role Not Set",
                description="Please set the jail role before using this command.",
                color=EMBED_COLOR_CODE
            )
            return await interaction.followup.send(embed=embed, ephemeral=True)

        if db.is_person_jailed(user.id):
            embed = discord.Embed(
                title="User Already Jailed",
                description=f"{user.mention} is already jailed.",
                color=EMBED_COLOR_CODE
            )
            return await interaction.followup.send(embed=embed, ephemeral=True)

        db.jail_user(user.id)

        for role in user.roles:
            if role != interaction.guild.default_role:
                await user.remove_roles(role)
                db.add_jail_role(user.id, role.id)

        jail_role = interaction.guild.get_role(await self.get_jail_role())
        await user.add_roles(jail_role)

        duration_text = "Indefinitely"
        total_minutes = (days * 24 * 60) + (hours * 60)
        if total_minutes > 0:
            duration_text = f"{days} days, {hours} hours"

        embed = discord.Embed(
            title="User Jailed",
            description=f"{user.mention} has been jailed.",
            color=discord.Color.red()
        )
        embed.add_field(name="Jailed By", value=interaction.user.mention, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Duration", value=duration_text, inline=False)

        await interaction.followup.send(embed=embed)

        log_channel = await self.get_log_channel(interaction.guild)
        if log_channel:
            await log_channel.send(embed=embed)

        # Send DM to the jailed user
        try:
            dm_embed = discord.Embed(
                title="You Have Been Jailed",
                description=f"You have been jailed in {interaction.guild.name}.",
                color=discord.Color.red()
            )
            dm_embed.add_field(name="Jailed By", value=interaction.user.name, inline=False)
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(name="Duration", value=duration_text, inline=False)
            
            await user.send(embed=dm_embed)
        except:
            # User might have DMs disabled
            pass

        if total_minutes > 0:
            await self.schedule_unjail(user, total_minutes)

    @app_commands.command(name="unjail", description="Unjail a user")
    async def unjail(self, interaction: discord.Interaction, user: discord.Member, reason: str = "-"):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "unjail"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
        
        # Create confirmation embed
        confirmation_embed = discord.Embed(
            title="Confirm Unjail",
            description=f"Are you sure you want to unjail {user.mention}?",
            color=discord.Color.green()
        )
        
        confirmation_embed.add_field(name="User", value=user.mention, inline=False)
        confirmation_embed.add_field(name="Reason", value=reason, inline=False)
        
        # Create confirmation view
        view = UnjailConfirmationView(
            cog=self,
            user=user,
            reason=reason,
            interaction=interaction
        )
        
        await interaction.response.send_message(embed=confirmation_embed, view=view, ephemeral=True)

    async def execute_unjail(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        """Execute the unjail action after confirmation"""
        user_db = User(user.id, user.name)
        db = database(DATABASE_FILE_PATH)
        db.add_user(user=user_db)

        if not await self.is_jail_role_set():
            embed = discord.Embed(
                title="Jail Role Not Set",
                description="Please set the jail role before using this command.",
                color=EMBED_COLOR_CODE
            )
            return await interaction.followup.send(embed=embed, ephemeral=True)

        if not db.is_person_jailed(user.id):
            embed = discord.Embed(
                title="User Not Jailed",
                description=f"{user.mention} is not jailed.",
                color=EMBED_COLOR_CODE
            )
            return await interaction.followup.send(embed=embed, ephemeral=True)

        db.unjail_user(user.id)

        jail_role = interaction.guild.get_role(await self.get_jail_role())
        await user.remove_roles(jail_role)

        jail_roles = db.get_jail_roles(user.id)
        for role_id in jail_roles:
            role = interaction.guild.get_role(role_id)
            if role:
                await user.add_roles(role)
                db.remove_jail_role(user.id, role_id)

        embed = discord.Embed(
            title="User Unjailed",
            description=f"{user.mention} has been unjailed.",
            color=discord.Color.green()
        )
        embed.add_field(name="Unjailed By", value=interaction.user.mention, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)

        await interaction.followup.send(embed=embed)

        log_channel = await self.get_log_channel(interaction.guild)
        if log_channel:
            await log_channel.send(embed=embed)
            
        # Send DM to the unjailed user
        try:
            dm_embed = discord.Embed(
                title="You Have Been Unjailed",
                description=f"You have been unjailed in {interaction.guild.name}.",
                color=discord.Color.green()
            )
            dm_embed.add_field(name="Unjailed By", value=interaction.user.name, inline=False)
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            
            await user.send(embed=dm_embed)
        except:
            # User might have DMs disabled
            pass


class JailConfirmationView(discord.ui.View):
    def __init__(self, cog, user, reason, days, hours, interaction):
        super().__init__(timeout=60)
        self.cog = cog
        self.user = user
        self.reason = reason
        self.days = days
        self.hours = hours
        self.original_interaction = interaction

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await self.cog.execute_jail(
            interaction=self.original_interaction,
            user=self.user,
            reason=self.reason,
            days=self.days,
            hours=self.hours
        )
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Jail command cancelled.", ephemeral=True)
        self.stop()


class UnjailConfirmationView(discord.ui.View):
    def __init__(self, cog, user, reason, interaction):
        super().__init__(timeout=60)
        self.cog = cog
        self.user = user
        self.reason = reason
        self.original_interaction = interaction

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await self.cog.execute_unjail(
            interaction=self.original_interaction,
            user=self.user,
            reason=self.reason
        )
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Unjail command cancelled.", ephemeral=True)
        self.stop()


async def setup(bot):
    await bot.add_cog(Jail(bot=bot))
