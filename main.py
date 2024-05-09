import asyncio
import logging
import discord
from discord.ext import commands
import traceback
import modules.helper.config as config
import modules.download as download
import signal
import sys
from modules.helper.logger import logger
from modules.queue import queue, manage_queue


# Create the client
client = commands.Bot(command_prefix=".", intents=discord.Intents.all())


# Load the cogs
async def load_cogs():
    for extension in extensions:
        try:
            await client.load_extension(extension)
            log.info(f"Loaded extension {extension}")
        except Exception as e:
            log.error(f"Failed to load extension {extension}: {e}")
            log.error(traceback.format_exc())


# Event for when the bot is ready
# Set the status and sync the tree
@client.event
async def on_ready():
    log.info(f"Logged in as {client.user}")
    # Set the status
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing, name="The Best Music"
        )
    )

    await client.tree.sync()
    await manage_queue.start()


# Handle Ctrl+C and terminate all processes safely
def signal_handler(sig, frame):
    log.info("Exiting")
    # Terminate all download processes
    download.terminate_processes()

    # Exit the program
    sys.exit(0)


def main():
    # Run the bot and load the cogs
    asyncio.run(load_cogs())

    # Initalize processes
    download.initalize_download_queue()

    client.run(config.DISCORD_TOKEN)

    # Handle Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    print("Press Ctrl+C to exit")


# Run the bot and load the cogs
if __name__ == "__main__":
    # Create a logger
    log = logging.getLogger("Dusic")

    extensions = [
        "modules.commands.music_control",
        "modules.ai",
    ]

    # Opus needed to play voice
    if not discord.opus.is_loaded():
        log.info("Loading Opus")
        discord.opus.load_opus(config.OPUS_PATH)

    main()
