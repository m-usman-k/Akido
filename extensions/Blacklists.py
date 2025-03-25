import discord, json
from discord.ext import commands
from discord import app_commands

from config import EMBED_COLOR_CODE
from config import BLACKLISTS_JSON_FILE_PATH
from functions.permissions import check_permission

class Blacklists(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="pw-blacklist-voice-channel", description="Blacklist a voice channel")
    async def pw_blacklist_voice_channel(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "pw-blacklist-voice-channel"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)

        try:
            with open(BLACKLISTS_JSON_FILE_PATH, "r") as f:
                data = json.load(f)

            if channel.id in data["blacklists"]["channels"]["voice"]:
                embed = discord.Embed(
                    title="Channel Already Blacklisted",
                    description=f"{channel.mention} is already blacklisted.",
                    color=0xFFA500
                )
                await interaction.response.send_message(embed=embed)
                return

            data["blacklists"]["channels"]["voice"].append(channel.id)
            with open(BLACKLISTS_JSON_FILE_PATH, "w") as f:
                json.dump(data, f, indent=4)

            embed = discord.Embed(
                title="Voice Channel Blacklisted",
                description=f"{channel.mention} has been blacklisted.",
                color=EMBED_COLOR_CODE
            )
            await interaction.response.send_message(embed=embed)

        except (json.JSONDecodeError, KeyError) as e:
            embed = discord.Embed(
                title="Error",
                description="There was an issue reading the blacklist file. Please check the file format.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="Unexpected Error",
                description=f"An error occurred: {str(e)}",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pw-whitelist-voice-channel", description="Whitelist a voice channel")
    async def pw_whitelist_voice_channel(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "pw-whitelist-voice-channel"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
        
        try:
            with open(BLACKLISTS_JSON_FILE_PATH, "r") as f:
                data = json.load(f)

            if channel.id not in data["blacklists"]["channels"]["voice"]:
                embed = discord.Embed(
                    title="Channel Not Blacklisted",
                    description=f"{channel.mention} is not blacklisted.",
                    color=0xFFA500
                )
                await interaction.response.send_message(embed=embed)
                return

            data["blacklists"]["channels"]["voice"].remove(channel.id)
            with open(BLACKLISTS_JSON_FILE_PATH, "w") as f:
                json.dump(data, f, indent=4)

            embed = discord.Embed(
                title="Voice Channel Whitelisted",
                description=f"{channel.mention} has been whitelisted.",
                color=EMBED_COLOR_CODE
            )
            await interaction.response.send_message(embed=embed)

        except (json.JSONDecodeError, KeyError) as e:
            embed = discord.Embed(
                title="Error",
                description="There was an issue reading the blacklist file. Please check the file format.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="Unexpected Error",
                description=f"An error occurred: {str(e)}",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pw-blacklist-text-channel", description="Blacklist a text channel")
    async def pw_blacklist_text_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "pw-blacklist-text-channel"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
        
        try:
            with open(BLACKLISTS_JSON_FILE_PATH, "r") as f:
                data = json.load(f)

            if channel.id in data["blacklists"]["channels"]["text"]:
                embed = discord.Embed(
                    title="Channel Already Blacklisted",
                    description=f"{channel.mention} is already blacklisted.",
                    color=0xFFA500
                )
                await interaction.response.send_message(embed=embed)
                return

            data["blacklists"]["channels"]["text"].append(channel.id)
            with open(BLACKLISTS_JSON_FILE_PATH, "w") as f:
                json.dump(data, f, indent=4)

            embed = discord.Embed(
                title="Text Channel Blacklisted",
                description=f"{channel.mention} has been blacklisted.",
                color=EMBED_COLOR_CODE
            )
            await interaction.response.send_message(embed=embed)

        except (json.JSONDecodeError, KeyError) as e:
            embed = discord.Embed(
                title="Error",
                description="There was an issue reading the blacklist file. Please check the file format.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="Unexpected Error",
                description=f"An error occurred: {str(e)}",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="pw-whitelist-text-channel", description="Whitelist a text channel")
    async def pw_whitelist_text_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "pw-whitelist-text-channel"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
        
        try:
            with open(BLACKLISTS_JSON_FILE_PATH, "r") as f:
                data = json.load(f)

            if channel.id not in data["blacklists"]["channels"]["text"]:
                embed = discord.Embed(
                    title="Channel Not Blacklisted",
                    description=f"{channel.mention} is not blacklisted.",
                    color=0xFFA500
                )
                await interaction.response.send_message(embed=embed)
                return

            data["blacklists"]["channels"]["text"].remove(channel.id)
            with open(BLACKLISTS_JSON_FILE_PATH, "w") as f:
                json.dump(data, f, indent=4)

            embed = discord.Embed(
                title="Text Channel Whitelisted",
                description=f"{channel.mention} has been whitelisted.",
                color=EMBED_COLOR_CODE
            )
            await interaction.response.send_message(embed=embed)

        except (json.JSONDecodeError, KeyError) as e:
            embed = discord.Embed(
                title="Error",
                description="There was an issue reading the blacklist file. Please check the file format.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="Unexpected Error",
                description=f"An error occurred: {str(e)}",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="pw-blacklist-user", description="Blacklist a user")
    async def pw_blacklist_user(self, interaction: discord.Interaction, user: discord.User):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "pw-blacklist-user"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
        
        try:
            with open(BLACKLISTS_JSON_FILE_PATH, "r") as f:
                data = json.load(f)

            if user.id in data["blacklists"]["users"]:
                embed = discord.Embed(
                    title="User Already Blacklisted",
                    description=f"{user.mention} is already blacklisted.",
                    color=0xFFA500
                )
                await interaction.response.send_message(embed=embed)
                return

            data["blacklists"]["users"].append(user.id)
            with open(BLACKLISTS_JSON_FILE_PATH, "w") as f:
                json.dump(data, f, indent=4)

            embed = discord.Embed(
                title="User Blacklisted",
                description=f"{user.mention} has been blacklisted.",
                color=EMBED_COLOR_CODE
            )
            await interaction.response.send_message(embed=embed)

        except (json.JSONDecodeError, KeyError) as e:
            embed = discord.Embed(
                title="Error",
                description="There was an issue reading the blacklist file. Please check the file format.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="Unexpected Error",
                description=f"An error occurred: {str(e)}",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pw-whitelist-user", description="Whitelist a user")
    async def pw_whitelist_user(self, interaction: discord.Interaction, user: discord.User):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "pw-whitelist-user"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
        
        try:
            with open(BLACKLISTS_JSON_FILE_PATH, "r") as f:
                data = json.load(f)

            if user.id not in data["blacklists"]["users"]:
                embed = discord.Embed(
                    title="User Not Blacklisted",
                    description=f"{user.mention} is not blacklisted.",
                    color=0xFFA500
                )
                await interaction.response.send_message(embed=embed)
                return

            data["blacklists"]["users"].remove(user.id)
            with open(BLACKLISTS_JSON_FILE_PATH, "w") as f:
                json.dump(data, f, indent=4)

            embed = discord.Embed(
                title="User Whitelisted",
                description=f"{user.mention} has been whitelisted.",
                color=EMBED_COLOR_CODE
            )
            await interaction.response.send_message(embed=embed)

        except (json.JSONDecodeError, KeyError) as e:
            embed = discord.Embed(
                title="Error",
                description="There was an issue reading the blacklist file. Please check the file format.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="Unexpected Error",
                description=f"An error occurred: {str(e)}",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pw-blacklist-role", description="Blacklist a role")
    async def pw_blacklist_role(self, interaction: discord.Interaction, role: discord.Role):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "pw-blacklist-role"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
        
        try:
            with open(BLACKLISTS_JSON_FILE_PATH, "r") as f:
                data = json.load(f)

            if role.id in data["blacklists"]["roles"]:
                embed = discord.Embed(
                    title="Role Already Blacklisted",
                    description=f"{role.mention} is already blacklisted.",
                    color=0xFFA500
                )
                await interaction.response.send_message(embed=embed)
                return

            data["blacklists"]["roles"].append(role.id)
            with open(BLACKLISTS_JSON_FILE_PATH, "w") as f:
                json.dump(data, f, indent=4)

            embed = discord.Embed(
                title="Role Blacklisted",
                description=f"{role.mention} has been blacklisted.",
                color=EMBED_COLOR_CODE
            )
            await interaction.response.send_message(embed=embed)

        except (json.JSONDecodeError, KeyError) as e:
            embed = discord.Embed(
                title="Error",
                description="There was an issue reading the blacklist file. Please check the file format.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="Unexpected Error",
                description=f"An error occurred: {str(e)}",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pw-whitelist-role", description="Whitelist a role")
    async def pw_whitelist_role(self, interaction: discord.Interaction, role: discord.Role):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "pw-whitelist-role"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
        
        try:
            with open(BLACKLISTS_JSON_FILE_PATH, "r") as f:
                data = json.load(f)

            if role.id not in data["blacklists"]["roles"]:
                embed = discord.Embed(
                    title="Role Not Blacklisted",
                    description=f"{role.mention} is not blacklisted.",
                    color=0xFFA500
                )
                await interaction.response.send_message(embed=embed)
                return

            data["blacklists"]["roles"].remove(role.id)
            with open(BLACKLISTS_JSON_FILE_PATH, "w") as f:
                json.dump(data, f, indent=4)

            embed = discord.Embed(
                title="Role Whitelisted",
                description=f"{role.mention} has been whitelisted.",
                color=EMBED_COLOR_CODE
            )
            await interaction.response.send_message(embed=embed)

        except (json.JSONDecodeError, KeyError) as e:
            embed = discord.Embed(
                title="Error",
                description="There was an issue reading the blacklist file. Please check the file format.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="Unexpected Error",
                description=f"An error occurred: {str(e)}",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pw-restrict-user" ,description="Restrict a user from getting the reward roles")
    async def pw_restrict_user(self, interaction: discord.Interaction, user: discord.User):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "pw-restrict-user"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
        
        try:
            with open(BLACKLISTS_JSON_FILE_PATH, "r") as f:
                data = json.load(f)

            if user.id in data["ineligible"]["users"]:
                embed = discord.Embed(
                    title="User Already Restricted",
                    description=f"{user.mention} is already restricted.",
                    color=0xFFA500
                )
                await interaction.response.send_message(embed=embed)
                return

            data["ineligible"]["users"].append(user.id)
            with open(BLACKLISTS_JSON_FILE_PATH, "w") as f:
                json.dump(data, f, indent=4)

            embed = discord.Embed(
                title="User Restricted",
                description=f"{user.mention} has been restricted.",
                color=EMBED_COLOR_CODE
            )
            await interaction.response.send_message(embed=embed)

        except (json.JSONDecodeError, KeyError) as e:
            embed = discord.Embed(
                title="Error",
                description="There was an issue reading the blacklist file. Please check the file format.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="Unexpected Error",
                description=f"An error occurred: {str(e)}",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="pw-unrestrict-user", description="Unrestrict a user from getting the reward roles")
    async def pw_unrestrict_user(self, interaction: discord.Interaction, user: discord.User):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "pw-unrestrict-user"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
        
        try:
            with open(BLACKLISTS_JSON_FILE_PATH, "r") as f:
                data = json.load(f)

            if user.id not in data["ineligible"]["users"]:
                embed = discord.Embed(
                    title="User Not Restricted",
                    description=f"{user.mention} is not restricted.",
                    color=0xFFA500
                )
                await interaction.response.send_message(embed=embed)
                return

            data["ineligible"]["users"].remove(user.id)
            with open(BLACKLISTS_JSON_FILE_PATH, "w") as f:
                json.dump(data, f, indent=4)

            embed = discord.Embed(
                title="User Unrestricted",
                description=f"{user.mention} has been unrestricted.",
                color=EMBED_COLOR_CODE
            )
            await interaction.response.send_message(embed=embed)

        except (json.JSONDecodeError, KeyError) as e:
            embed = discord.Embed(
                title="Error",
                description="There was an issue reading the blacklist file. Please check the file format.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="Unexpected Error",
                description=f"An error occurred: {str(e)}",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pw-restrict-role", description="Restrict a role from getting the reward roles")
    async def pw_restrict_role(self, interaction: discord.Interaction, role: discord.Role):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "pw-restrict-role"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
        
        try:
            with open(BLACKLISTS_JSON_FILE_PATH, "r") as f:
                data = json.load(f)

            if role.id in data["ineligible"]["roles"]:
                embed = discord.Embed(
                    title="Role Already Restricted",
                    description=f"{role.mention} is already restricted.",
                    color=0xFFA500
                )
                await interaction.response.send_message(embed=embed)
                return

            data["ineligible"]["roles"].append(role.id)
            with open(BLACKLISTS_JSON_FILE_PATH, "w") as f:
                json.dump(data, f, indent=4)

            embed = discord.Embed(
                title="Role Restricted",
                description=f"{role.mention} has been restricted.",
                color=EMBED_COLOR_CODE
            )
            await interaction.response.send_message(embed=embed)

        except (json.JSONDecodeError, KeyError) as e:
            embed = discord.Embed(
                title="Error",
                description="There was an issue reading the blacklist file. Please check the file format.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="Unexpected Error",
                description=f"An error occurred: {str(e)}",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pw-unrestrict-role", description="Unrestrict a role from getting the reward roles")
    async def pw_unrestrict_role(self, interaction: discord.Interaction, role: discord.Role):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "pw-unrestrict-role"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
        
        try:
            with open(BLACKLISTS_JSON_FILE_PATH, "r") as f:
                data = json.load(f)

            if role.id not in data["ineligible"]["roles"]:
                embed = discord.Embed(
                    title="Role Not Restricted",
                    description=f"{role.mention} is not restricted.",
                    color=0xFFA500
                )
                await interaction.response.send_message(embed=embed)
                return

            data["ineligible"]["roles"].remove(role.id)
            with open(BLACKLISTS_JSON_FILE_PATH, "w") as f:
                json.dump(data, f, indent=4)

            embed = discord.Embed(
                title="Role Unrestricted",
                description=f"{role.mention} has been unrestricted.",
                color=EMBED_COLOR_CODE
            )
            await interaction.response.send_message(embed=embed)

        except (json.JSONDecodeError, KeyError) as e:
            embed = discord.Embed(
                title="Error",
                description="There was an issue reading the blacklist file. Please check the file format.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="Unexpected Error",
                description=f"An error occurred: {str(e)}",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pw-blacklist-info", description="Get information about the blacklists of poweruser function")
    async def pw_blacklist_info(self, interaction: discord.Interaction):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "pw-blacklist-info"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
        
        try:
            with open(BLACKLISTS_JSON_FILE_PATH, "r") as f:
                data = json.load(f)

            text_channels = [interaction.guild.get_channel(channel_id) for channel_id in data["blacklists"]["channels"]["text"]]
            voice_channels = [interaction.guild.get_channel(channel_id) for channel_id in data["blacklists"]["channels"]["voice"]]
            users = [interaction.guild.get_member(user_id) for user_id in data["blacklists"]["users"]]
            roles = [interaction.guild.get_role(role_id) for role_id in data["blacklists"]["roles"]]
            ineligible_users = [interaction.guild.get_member(user_id) for user_id in data["ineligible"]["users"]]
            ineligible_roles = [interaction.guild.get_role(role_id) for role_id in data["ineligible"]["roles"]]

            embed = discord.Embed(
                title="Blacklist Information",
                color=EMBED_COLOR_CODE
            )

            embed.add_field(
                name="Text Channels",
                value="\n".join([channel.mention for channel in text_channels if channel]) if text_channels else "None"
            )

            embed.add_field(
                name="Voice Channels",
                value="\n".join([channel.mention for channel in voice_channels if channel]) if voice_channels else "None"
            )

            embed.add_field(
                name="Users",
                value="\n".join([user.mention for user in users if user]) if users else "None"
            )

            embed.add_field(
                name="Roles",
                value="\n".join([role.mention for role in roles if role]) if roles else "None"
            )

            embed.add_field(
                name="Ineligible Users",
                value="\n".join([user.mention for user in ineligible_users if user]) if ineligible_users else "None"
            )

            embed.add_field(
                name="Ineligible Roles",
                value="\n".join([role.mention for role in ineligible_roles if role]) if ineligible_roles else "None"
            )

            await interaction.response.send_message(embed=embed)

        except (json.JSONDecodeError, KeyError) as e:
            embed = discord.Embed(
                title="Error",
                description="There was an issue reading the blacklist file. Please check the file format.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="Unexpected Error",
                description=f"An error occurred: {str(e)}",
                color=0xFF0000
            )
            return await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Blacklists(bot=bot))
