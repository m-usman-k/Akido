import json
from discord import Interaction

from config import SUPREME_USER
from config import PERMISSIONS_JSON_FILE_PATH

async def check_permission(interaction: Interaction, command_name: str) -> bool:
    """
    Check if a user has permission to use a command.
    
    Args:
        interaction: The Discord interaction object
        command_name: The name of the command to check
        
    Returns:
        bool: True if user has permission, False otherwise
    """
    # Supreme user always has permission
    if interaction.user.id == SUPREME_USER:
        return True
    
    # Load permissions
    try:
        with open(PERMISSIONS_JSON_FILE_PATH, 'r') as f:
            permissions = json.load(f)
        
        # Check if command exists in permissions
        for cmd in permissions:
            if cmd["command"] == command_name:
                # Check if user is in allowed users
                if interaction.user.id in cmd["users"]:
                    return True
                
                # Check if user has any of the allowed roles
                for role_id in cmd["roles"]:
                    if interaction.guild and any(role.id == role_id for role in interaction.user.roles):
                        return True
                
                # If we got here, user doesn't have permission
                return False
        
        # If command not in permissions, default to allow (or you could default to deny)
        return True
    except Exception as e:
        print(f"Error checking permissions: {e}")
        # Default to allow on error to prevent lockouts
        return True

async def initialize_permissions(bot) -> None:
    """
    Initialize the permissions system with all available commands.
    
    Args:
        bot: The Discord bot instance
    """
    # Get all commands from all cogs
    all_commands = []
    for cog_name, cog in bot.cogs.items():
        for command in cog.get_app_commands():
            all_commands.append(command.name)
    
    # Load current permissions
    try:
        with open(PERMISSIONS_JSON_FILE_PATH, "r") as f:
            current_permissions = json.load(f)
    except:
        current_permissions = []
    
    # Add any missing commands
    current_command_names = [cmd["command"] for cmd in current_permissions]
    for command_name in all_commands:
        if command_name not in current_command_names:
            current_permissions.append({
                "command": command_name,
                "users": [],
                "roles": []
            })
    
    # Save back to file
    with open(PERMISSIONS_JSON_FILE_PATH, "w") as f:
        json.dump(current_permissions, f, indent=4)
    
    print(f"Permissions initialized with {len(all_commands)} commands")