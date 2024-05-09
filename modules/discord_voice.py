from discord import FFmpegPCMAudio
from modules.helper.class_types import Music, GuildQueue
from modules.helper.embeds import now_playing_embed
import modules.helper.config as config
import asyncio
import os


class Play_On_Discord:
    # Play music on the voice channel
    async def play(music: Music, queue: dict):
        # Connect to voice channel, try and see if its already connected
        voice_channel = music.voice_channel
        voice_client = music.voice_channel.guild.voice_client

        # If the voice client is None, then connect to the voice channel
        if voice_client == None:
            voice_client = await voice_channel.connect()

        # Wait for the music to be downloaded
        while (
            music.file_name == None
            or music.file_name == "downloading"
            or not os.path.exists(config.MUSIC_FOLDER + music.file_name)
        ):
            await asyncio.sleep(1)

        # Send embed
        await music.interaction.channel.send(embed=await now_playing_embed(music))

        # Save voice client
        music.set_data(voice_client=voice_client)

        # Load the music and play it
        source = FFmpegPCMAudio(config.MUSIC_FOLDER + music.file_name)

        player = voice_client.play(source)

        music.set_data(ffmpeg_process=source)

        while queue[music.interaction.guild_id].currently_playing != None:
            # The three checks are necessary to ensure that the bot stops playing music
            # First check is to see if the bot is playing music
            # Second is to check if the music is paused by user request
            # Third is to check that the music wasn't skipped by skip or clear command because they will set currently playing to none
            if voice_client.is_playing() == False and voice_client.is_paused() == False:
                Play_On_Discord.stop_music(music, queue)
                break

            await asyncio.sleep(1)

    def stop_music(music: Music, queue: GuildQueue, leave_channel: bool = False):
        queue.currently_playing = None
        queue.music.remove(music)

        music.voice_client.stop()
        music.ffmpeg_process.cleanup()

        if leave_channel:
            music.voice_client.disconnect()
