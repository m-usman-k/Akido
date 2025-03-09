import discord, json
from discord.ext import commands
from discord import app_commands

from functions.database import database

from structures.User import User

from config import EMBED_COLOR_CODE
from config import DATABASE_FILE_PATH
from config import DEFAULTS_JSON_FILE_PATH


class Jail(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def is_jail_role_set(self):
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)

        if data["jail_role"] == 0:
            return False
        else:
            return True
        
    async def is_person_jailed(self, user_id: int):
        db = database(DATABASE_FILE_PATH)
        return db.is_person_jailed(user_id)
    
    async def get_jail_role(self):
        with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
            data = json.load(file)

        return data["jail_role"]
    

    @app_commands.command(name="jail", description="Jail a user")
    async def jail(self, interaction: discord.Interaction, user: discord.User, reason: str):

        user_db = User(user.id, user.name)
        db = database(DATABASE_FILE_PATH)
        db.add_user(user=user_db)

        if not await self.is_jail_role_set():
            embed = discord.Embed(
                title="Jail Role Not Set",
                description="Please set the jail role before using this command.",
                color=EMBED_COLOR_CODE
            )

            await interaction.response.send_message(embed=embed)
            return
        
        if await self.is_person_jailed(user.id):
            embed = discord.Embed(
                title="User Already Jailed",
                description=f"{user.mention} is already jailed.",
                color=EMBED_COLOR_CODE
            )

            await interaction.response.send_message(embed=embed)
            return

        db = database(DATABASE_FILE_PATH)
        db.jail_user(user.id)

        for role in user.roles:
            if role != interaction.guild.default_role:
                await user.remove_roles(role)
                db.add_jail_role(user.id, role.id)

        jail_role = interaction.guild.get_role(await self.get_jail_role())
        await user.add_roles(jail_role)

        embed = discord.Embed(
            title="User Jailed",
            description=f"{user.mention} has been jailed.",
            color=EMBED_COLOR_CODE
        )
        embed.add_field(name="Reason", value=reason, inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="unjail", description="Unjail a user")
    async def unjail(self, interaction: discord.Interaction, user: discord.User, reason: str):
        user_db = User(user.id, user.name)
        db = database(DATABASE_FILE_PATH)
        db.add_user(user=user_db)

        if not await self.is_jail_role_set():
            embed = discord.Embed(
                title="Jail Role Not Set",
                description="Please set the jail role before using this command.",
                color=EMBED_COLOR_CODE
            )

            await interaction.response.send_message(embed=embed)
            return
        
        if not await self.is_person_jailed(user.id):
            embed = discord.Embed(
                title="User Not Jailed",
                description=f"{user.mention} is not jailed.",
                color=EMBED_COLOR_CODE
            )

            await interaction.response.send_message(embed=embed)
            return

        db = database(DATABASE_FILE_PATH)
        db.unjail_user(user.id)

        jail_role = interaction.guild.get_role(await self.get_jail_role())
        await user.remove_roles(jail_role)

        jail_roles = db.get_jail_roles(user.id)
        for role_id in jail_roles:
            role = interaction.guild.get_role(role_id)
            await user.add_roles(role)
            db.remove_jail_role(user.id, role_id)

        embed = discord.Embed(
            title="User Unjailed",
            description=f"{user.mention} has been unjailed.",
            color=EMBED_COLOR_CODE
        )
        embed.add_field(name="Reason", value=reason, inline=False)

        await interaction.response.send_message(embed=embed)
        

    @app_commands.command(name="set-jail-role", description="Set the jail role")
    async def set_jail_role(self, interaction: discord.Interaction, role: discord.Role):
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


async def setup(bot):
    await bot.add_cog(Jail(bot=bot))