import discord, json
from discord.ext import commands
from discord import app_commands

from config import EMBED_COLOR_CODE
from config import BLACKLISTS_JSON_FILE_PATH


class Blacklists(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="blacklist-voice-channel-add" , description="Blacklist a voice channel")
    async def blacklist_voice_channel_add(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        with open(BLACKLISTS_JSON_FILE_PATH, "r") as f:
            data = json.load(f)

        data["blacklist"]["channels"]["voice"].append(channel.id)

        with open(BLACKLISTS_JSON_FILE_PATH, "w") as f:
            json.dump(data, f, indent=4)

        embed = discord.Embed(
            title="Voice Channel Blacklisted",
            description=f"{channel.name} has been blacklisted",
            color=EMBED_COLOR_CODE
        )

        await interaction.response.send_message(embed=embed)

    

    


async def setup(bot):
    await bot.add_cog(Blacklists(bot=bot))