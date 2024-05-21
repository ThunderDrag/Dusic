import logging
import discord
import asyncio
import signal
import os
from discord.ext import commands
from modules import download, queue, error_handler
from modules.helper import config, logger

# Set up logging
log = logging.getLogger(config.LOGGER_NAME)

extensions = [
    "modules.commands.music_commands",
    "modules.ai",
    "modules.discord_voice_afk",
]

# Create a new bot instance
client = commands.Bot(command_prefix="!", intents=discord.Intents.all())



async def load_cogs():
    for extension in extensions:
        await client.load_extension(extension)
        log.info(f"Loaded extension {extension}")


def terminate_processes(sig, frame):
    log.info("Terminating processes")
    download.terminate_processes()
    exit(0)

@client.event
async def on_ready():
    log.info(f"Logged in as {client.user}")
    # Set the bot's status
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing, name="The Best Music"
        )
    )
    
    await client.tree.sync()
    await queue.manage_queue.start()


# Set up the bot and run it
if __name__ == "__main__":
    # Load OPUS
    if not discord.opus.is_loaded():
        discord.opus.load_opus(config.OPUS_PATH)
        log.info("Loaded OPUS")
    
    
    # Create download processes
    download.initalize_download_queue()
    
    
    # Handle program termination to make sure all the processes are terminated
    signal.signal(signal.SIGINT, terminate_processes)
    
    
    # Load the extensions
    asyncio.run(load_cogs())
    
    # If music folder does not exist, create it
    if not os.path.exists(config.MUSIC_FOLDER):
        os.mkdir(config.MUSIC_FOLDER)
    
    client.run(config.DISCORD_TOKEN)
    