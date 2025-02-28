import discord, os
from discord.ext import commands
from dotenv import load_dotenv

from functions.database import database

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("🟡 | Bot is starting")

    print("🟡 | Checking permissions")
    if not os.path.exists("./database/permissions.json"):
        print("🔴 | Permissions file not found")
        print("🟡 | Creating permissions file")
        with open("./database/permissions.json", "w") as f:
            f.write("{}")
        print("🟢 | Permissions file created")


    print("🟡 | Connecting to database")
    db = database('./database/database.db')

    print("🟡 | Loading all extensions")
    await bot.load_extension("extensions.Permissions")


    
    

    await bot.tree.sync()
    print("🟢 | Bot is live")


bot.run(BOT_TOKEN)