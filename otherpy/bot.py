import discord
from discord.ext import commands
from otherpy.keep_alive import keep_alive  # Import the keep-alive script
import os
TOKEN = os.getenv("DISCORD_TOKEN")

# Set up bot intents
intents = discord.Intents.default()
intents.messages = True  # Ensure the bot can receive messages

# Initialize bot with a command prefix (e.g., "!")
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Example command
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Start the keep-alive server
keep_alive()

# Run the bot (this will run in a separate thread in app.py)
# This should be removed if Flask and Discord bot are already running in separate threads.
# bot.run(TOKEN)
