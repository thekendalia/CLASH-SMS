import discord
from discord.ext import commands, tasks
from otherpy.keep_alive import keep_alive  # Import the keep-alive script
import os
import asyncio
from otherpy.utils import count

TOKEN = os.getenv("DISCORD_TOKEN")

# Set up bot intents
intents = discord.Intents.default()
intents.messages = True  # Ensure the bot can receive messages

# Initialize bot with a command prefix (e.g., "!")
bot = commands.Bot(command_prefix="!", intents=intents)

@tasks.loop(minutes=10)
async def update_status():
    member_count = count()  # Call count() to get the actual value
    status_message = f"{member_count} members"
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status_message))
    print(f"Status updated to: {status_message}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    update_status.start()  # Start the loop when bot is ready

# Example command
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Start the keep-alive server
keep_alive()

# Run the bot (this will run in a separate thread in app.py)
# bot.run(TOKEN)
