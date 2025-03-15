import discord
from discord.ext import commands
from discord import app_commands

from functions.permissions import check_permission

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    # Commands:
    @app_commands.command(name="help", description="A command to display all the commands available.")
    async def help(self, interaction: discord.Interaction):
        # Check if user has permission to use this command
        if not await check_permission(interaction, "help"):
            return await interaction.response.send_message("🔴 You do not have permission to use this command 🔴", ephemeral=True)
        
        # Create the main embed
        main_embed = discord.Embed(
            title="Bot Help",
            description="Select a category from the dropdown menu below to view available commands.",
            color=discord.Color.blue()
        )
        
        # Create the dropdown view
        view = HelpView(self.bot, interaction)
        
        await interaction.response.send_message(embed=main_embed, view=view)


class HelpView(discord.ui.View):
    def __init__(self, bot, interaction):
        super().__init__(timeout=60)
        self.bot = bot
        self.interaction = interaction
        self.add_item(HelpSelect(bot, interaction))


class HelpSelect(discord.ui.Select):
    def __init__(self, bot, interaction):
        self.bot = bot
        self.interaction = interaction
        
        # Get all cogs except Events
        options = []
        for cog_name in bot.cogs:
            if cog_name != "Events":  # Skip Events cog
                options.append(discord.SelectOption(
                    label=cog_name,
                    description=f"View commands for {cog_name}",
                    value=cog_name
                ))
        
        super().__init__(placeholder="Select a category...", options=options)

    async def callback(self, interaction: discord.Interaction):
        """Handles the help category selection."""
        if interaction.user.id != self.interaction.user.id:
            return await interaction.response.send_message("You can't interact with this menu!", ephemeral=True)
        
        selected_cog_name = self.values[0]
        cog = self.bot.get_cog(selected_cog_name)
        
        if not cog:
            return await interaction.response.send_message(f"Cog {selected_cog_name} not found.", ephemeral=True)
        
        # Create embed for the selected cog
        embed = discord.Embed(
            title=f"{selected_cog_name} Commands",
            description=f"Here are the commands available in the {selected_cog_name} category:",
            color=discord.Color.blue()
        )
        
        # Add commands to the embed
        for command in cog.get_app_commands():
            # Format parameters
            params = []
            for param in command.parameters:
                if param.required:
                    params.append(f"<{param.name}>")
                else:
                    params.append(f"[{param.name}]")
            
            param_str = " ".join(params)
            
            # Add command to embed
            embed.add_field(
                name=f"/{command.name} {param_str}",
                value=command.description or "No description provided",
                inline=False
            )
        
        # If no commands found
        if len(embed.fields) == 0:
            embed.description = f"No commands found in the {selected_cog_name} category."
        
        await interaction.response.edit_message(embed=embed, view=self.view)


async def setup(bot):
    await bot.add_cog(Help(bot=bot))