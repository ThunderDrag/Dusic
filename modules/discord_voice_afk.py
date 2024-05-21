import discord
import logging
import asyncio
from discord.ext import commands
from modules import discord_voice
from modules.queue import queue
from modules.helper import config


log = logging.getLogger(config.LOGGER_NAME)


class Kicked(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member == self.bot.user and before.channel is not None and after.channel is None:
            pass
        else:
            return
        
        guild_id = member.guild.id
        queue.empty_queue(member.guild.id)
        
        if(queue.is_playing(guild_id)):
            discord_voice.stop_music(queue.queue[guild_id])


class VoiceChannelChanged(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member == self.bot.user and before.channel is not None and after.channel is not None and before.channel != after.channel:
            pass
        else:
            return
        
        guild_id = member.guild.id
        queue.ensure_guild_in_queue(guild_id)

        # First we check if the bot is playing music in the guild
        if not queue.is_playing(guild_id):
            return

        # Check if the bot was playing music in the previous voice channel
        if(queue.queue[guild_id].current_music.voice_channel == after.channel):
            return        

        # Update the voice channel of all the music in the queue
        for music in queue.queue[guild_id].music:
            music.voice_channel = after.channel

        # If the bot was playing music, we need to move the bot to the new voice channel
        music = queue.queue[guild_id].current_music

        # We set the voice channel changing to true, so that the bot doesn't stop the music
        music.set_data(voice_channel_changing=True)
        
        queue.queue[guild_id].current_music = music

        # Disconnect from the previous channel and stop ffmpeg process
        music.voice_client.stop()
        await music.voice_client.disconnect()
        music.ffmpeg_process.cleanup()
        
        
        while not after.channel.guild.voice_client.is_connected():
            await asyncio.sleep(0.1)
        
        voice_client = after.channel.guild.voice_client
        
        options = {
            'options': f'-ss {music.position}'
        }
        
        ffmpeg_process = discord.FFmpegPCMAudio(music.file_path, options=options)        
        voice_client.play(ffmpeg_process, after=discord_voice.create_after_callback(queue.queue[guild_id]))
        
        
        music.set_data(
            voice_client=voice_client,
            voice_channel=after.channel,
            ffmpeg_process=ffmpeg_process,
            voice_channel_changing=False
        )
        queue.queue[guild_id].current_music = music


async def setup(bot: commands.Bot):
    await bot.add_cog(Kicked(bot))
    await bot.add_cog(VoiceChannelChanged(bot))