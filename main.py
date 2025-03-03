import discord, os
from discord.ext import commands
from dotenv import load_dotenv

from functions.database import database

from config import BOT_PREFIX
from config import DATABASE_FILE_PATH
from config import BLACKLISTS_JSON_FILE_PATH
from config import PERMISSIONS_JSON_FILE_PATH

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("🟡 | Bot is starting")

    print("🟡 | Checking permissions")
    if not os.path.exists(PERMISSIONS_JSON_FILE_PATH):
        print("🔴 | Permissions file not found")
        print("🟡 | Creating permissions file")
        with open(PERMISSIONS_JSON_FILE_PATH, "w") as f:
            f.write("[]")
        print("🟢 | Permissions file created")

    if not os.path.exists(BLACKLISTS_JSON_FILE_PATH):
        print("🔴 | Blacklists file not found")
        print("🟡 | Creating blacklists file")
        with open(BLACKLISTS_JSON_FILE_PATH, "w") as f:
            f.write("[]")
        print("🟢 | Blacklists file created")


    print("🟡 | Connecting to database")
    db = database(DATABASE_FILE_PATH)
    db.close()
    print("🟢 | Connected to database")

    print("🟡 | Loading all extensions")
    await bot.load_extension("extensions.Help")
    await bot.load_extension("extensions.Events")
    await bot.load_extension("extensions.Leaderboard")
    await bot.load_extension("extensions.Permissions")
    print("🟢 | All extensions loaded")

    print("🟡 | Syncing tree")
    await bot.tree.sync()
    print("🟢 | Tree synced")

    print("🟢 | Bot is live")


bot.run(BOT_TOKEN)