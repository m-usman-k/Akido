import discord, json
from discord.ext import commands
from discord import app_commands

from config import SUPREME_USER
from config import EMBED_COLOR_CODE
from config import PERMISSIONS_JSON_FILE_PATH

from functions.permissions import check_permission, initialize_permissions

class Permissions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    # Commands:
    @app_commands.command(name="display-permissions", description="Displays permissions of users and roles for a specific command.")
    async def display_permissions(self, interaction: discord.Interaction):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "display-permissions"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
            
        if interaction.user.id != SUPREME_USER:
            return await interaction.response.send_message("🔴 This Command Is Forbidden For You ���", ephemeral=False)

        with open(PERMISSIONS_JSON_FILE_PATH, "r") as f:
            all_permissions = json.load(f)

        commands_list = [cmd["command"] for cmd in all_permissions]
        view = PermissionsView(commands_list)

        await interaction.response.send_message("Select a command to view its permissions:", view=view, ephemeral=False)
        
    @app_commands.command(name="initialize-permissions", description="Initialize the permissions system with all available commands.")
    async def initialize_permissions_command(self, interaction: discord.Interaction):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "initialize-permissions"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
            
        if interaction.user.id != SUPREME_USER:
            return await interaction.response.send_message("🔴 This Command Is Forbidden For You 🔴", ephemeral=True)
        
        await initialize_permissions(self.bot)
        
        embed = discord.Embed(
            title="Permissions Initialized",
            description="All commands have been added to the permissions system.",
            color=EMBED_COLOR_CODE
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="set-permission", description="A command to set permissions of users and roles to certain commands.")
    async def set_permission(self, interaction: discord.Interaction, role: discord.Role = None, user: discord.User = None):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "set-permission"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
            
        if interaction.user.id != SUPREME_USER:
            return await interaction.response.send_message("🔴This Command Is Forbidden For You🔴")

        if not role and not user:
            return await interaction.response.send_message("🔴 You must specify either a role or a user. 🔴", ephemeral=True)

        with open(PERMISSIONS_JSON_FILE_PATH, "r") as f:
            all_permissions = json.load(f)

        commands_list = [cmd["command"] for cmd in all_permissions]
        view = PermissionActionView(commands_list, role, user)

        await interaction.response.send_message("Select an action:", view=view, ephemeral=True)

# Views:
class PermissionsView(discord.ui.View):
    def __init__(self, commands_list):
        super().__init__()
        self.add_item(PermissionsDropdown(commands_list))

class PermissionActionView(discord.ui.View):
    def __init__(self, commands_list, role, user):
        super().__init__()
        self.add_item(PermissionActionDropdown(commands_list, role, user))

# Select Menus:
class PermissionsDropdown(discord.ui.Select):
    def __init__(self, commands_list):
        options = [discord.SelectOption(label=cmd, value=cmd) for cmd in commands_list]
        super().__init__(placeholder="Select a command...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        with open(PERMISSIONS_JSON_FILE_PATH, "r") as f:
            all_permissions = json.load(f)

        selected_command = self.values[0]
        for each_command in all_permissions:
            if each_command["command"] == selected_command:
                user_ids = each_command["users"]
                role_ids = each_command["roles"]

                user_mentions = "\n".join([interaction.guild.get_member(uid).mention for uid in user_ids if interaction.guild.get_member(uid)]) or "None"
                role_mentions = "\n".join([interaction.guild.get_role(rid).mention for rid in role_ids if interaction.guild.get_role(rid)]) or "None"

                embed = discord.Embed(title=f"Permissions for `/{selected_command}`", color=EMBED_COLOR_CODE)
                embed.add_field(name="Allowed Users", value=user_mentions, inline=False)
                embed.add_field(name="Allowed Roles", value=role_mentions, inline=False)

                await interaction.response.edit_message(embed=embed, view=None, content="")
                return

class PermissionActionDropdown(discord.ui.Select):
    def __init__(self, commands_list, role, user):
        self.commands_list = commands_list
        self.role = role
        self.user = user
        options = [
            discord.SelectOption(label="Add Permission", value="add"),
            discord.SelectOption(label="Remove Permission", value="remove")
        ]
        super().__init__(placeholder="Select an action...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        action = self.values[0]
        if action == "remove":
            with open(PERMISSIONS_JSON_FILE_PATH, "r") as f:
                all_permissions = json.load(f)
            if self.user:
                commands_list = [cmd["command"] for cmd in all_permissions if self.user.id in cmd["users"]]
                if not commands_list:
                    embed = discord.Embed(title="No Permissions", description=f"{self.user.mention} does not have permission for any command.", color=EMBED_COLOR_CODE)
                    return await interaction.response.send_message(embed=embed, ephemeral=True)
            elif self.role:
                commands_list = [cmd["command"] for cmd in all_permissions if self.role.id in cmd["roles"]]
                if not commands_list:
                    embed = discord.Embed(title="No Permissions", description=f"{self.role.mention} does not have permission for any command.", color=EMBED_COLOR_CODE)
                    return await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            commands_list = self.commands_list
        view = CommandSelectionView(commands_list, self.role, self.user, action)
        await interaction.response.edit_message(content="Select a command:", view=view)

class CommandSelectionView(discord.ui.View):
    def __init__(self, commands_list, role, user, action):
        super().__init__()
        self.add_item(CommandSelectionDropdown(commands_list, role, user, action))

class CommandSelectionDropdown(discord.ui.Select):
    def __init__(self, commands_list, role, user, action):
        self.role = role
        self.user = user
        self.action = action
        options = [discord.SelectOption(label=cmd, value=cmd) for cmd in commands_list]
        super().__init__(placeholder="Select a command...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        selected_command = self.values[0]

        with open(PERMISSIONS_JSON_FILE_PATH, "r") as f:
            all_permissions = json.load(f)

        for each_command in all_permissions:
            if each_command["command"] == selected_command:
                if self.action == "add":
                    if self.role:
                        if self.role.id not in each_command["roles"]:
                            each_command["roles"].append(self.role.id)
                    if self.user:
                        if self.user.id not in each_command["users"]:
                            each_command["users"].append(self.user.id)
                elif self.action == "remove":
                    if self.role:
                        if self.role.id in each_command["roles"]:
                            each_command["roles"].remove(self.role.id)
                    if self.user:
                        if self.user.id in each_command["users"]:
                            each_command["users"].remove(self.user.id)

        with open(PERMISSIONS_JSON_FILE_PATH, "w") as f:
            json.dump(all_permissions, f, indent=4)

        embed = discord.Embed(title=f"Permissions {self.action}ed", color=EMBED_COLOR_CODE)
        embed.add_field(name="Command", value=f"/{selected_command}", inline=False)
        if self.role:
            embed.add_field(name="Role", value=self.role.mention, inline=False)
        if self.user:
            embed.add_field(name="User", value=self.user.mention, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Permissions(bot=bot))

