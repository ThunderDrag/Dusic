import discord
from discord.ext import tasks
import logging
from typing import Dict
from modules.helper.class_types import Music, GuildQueue
from modules.discord_voice import Play_On_Discord
import modules.download as download
import asyncio

# Create a logger
logger = logging.getLogger("Dusic")


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

        if self.queue[guildID].currently_playing == None:
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


queue = Queue()


@tasks.loop(seconds=1)
async def manage_queue():
    # Iterate over all guilds
    for guildID in queue.queue:
        # Iterate over music
        for i, music in enumerate(queue.queue[guildID].music):
            # Only prepare upto 5 songs
            if i >= 5:
                break

            # If the music is not downloaded, download it
            if music.file_name == None:
                asyncio.create_task(download.ensure_music_is_downloaded(music))

            # If the bot is not playing any music, then play the music
            if queue.queue[guildID].currently_playing == None:
                asyncio.create_task(Play_On_Discord.play(music, queue.queue))
                queue.queue[guildID].currently_playing = music
