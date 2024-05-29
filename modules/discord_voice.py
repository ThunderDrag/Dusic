import os
import asyncio
import discord
import logging
from modules.helper import embeds, config
from modules.helper.types import Music, GuildQueue


log = logging.getLogger(config.LOGGER_NAME)


# Play music on voice channel
async def play_music(music: Music, queue: GuildQueue):
    # Connect to voice channel, try and see if its already connected
    voice_channel = music.voice_channel
    voice_client = music.voice_channel.guild.voice_client

    # Wait for the music to be downloaded
    while (
        music.file_path == None
        or music.file_path == "downloading"
        or not os.path.exists(music.file_path)
    ):
        await asyncio.sleep(0.1)


    # If the voice client is None, then connect to the voice channel
    if voice_client == None:
        voice_client = await voice_channel.connect()

    # Send embed
    await music.context.send(embed=await embeds.now_playing(music))

    # Load the music and play it
    source = discord.FFmpegPCMAudio(music.file_path)

    # Play the music
    if(voice_client.is_playing()):
        voice_client.stop()
    
    voice_client.play(source, after=create_after_callback(queue))

    # Save the voice client and ffmpeg process
    music.set_data(voice_client=voice_client, ffmpeg_process=source)


def create_after_callback(queue: GuildQueue):
    def after_callback(error):
        stop_music(queue)
    return after_callback


# Stop music on voice channel
def stop_music(queue: GuildQueue):
    music = queue.current_music
    
    if music is None or music.voice_channel_changing == True:
        return

    # Clear the current music and remove it from the queue
    queue.current_music = None
    try:
        queue.music.remove(music)
    except:
        pass

    # Stop the music and cleanup the ffmpeg process
    try:
        music.voice_client.stop()
    except Exception as e:
        pass