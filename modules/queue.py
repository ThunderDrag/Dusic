import logging
import asyncio
from typing import Dict
from discord.ext import tasks
from modules.helper import config
from modules.helper.types import Music, GuildQueue
from modules import download, discord_voice


# Setup Logger
log = logging.getLogger(config.LOGGER_NAME)



class Queue:
    def __init__(self):
        self.queue: Dict[str, GuildQueue] = {}

    # Add music to the queue
    async def add_music(self, guildID: str, music: Music):
        self.ensure_guild_in_queue(guildID)
        self.queue[guildID].music.append(music)

    # Find out if the bot is playing music in a guild
    def is_playing(self, guildID: str):
        self.ensure_guild_in_queue(guildID)

        if self.queue[guildID].current_music == None:
            return False

        return True

    # Ensure that the guild is in the queue, if not then add it
    def ensure_guild_in_queue(self, guildID: str):
        if guildID not in self.queue:
            self.queue[guildID] = GuildQueue()

    # Get the queue length
    def get_queue_length(self, guildID: str):
        if guildID not in self.queue:
            return 0

        return len(self.queue[guildID].music)
    
    # Empty the queue
    def empty_queue(self, guildID: str):
        # Ensure that the guild is in the queue
        self.ensure_guild_in_queue(guildID)
        
        self.queue[guildID].music = []



@tasks.loop(seconds=0.1)
async def manage_queue():
    # Iterate over all guilds
    q = queue.queue
    for guildID in q:
        # Iterate over music
        for i, music in enumerate(q[guildID].music):
            # Only prepare upto 5 songs
            if i >= 5:
                break

            # If the music is not downloaded, download it
            if music.file_path == None:
                asyncio.create_task(download.ensure_music_is_downloaded(music))

            # If the bot is not playing any music, then play the music
            if q[guildID].current_music == None:
                asyncio.create_task(discord_voice.play_music(music, q[guildID]))
                queue.queue[guildID].current_music = music



queue = Queue()




