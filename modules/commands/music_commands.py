import discord
import logging
from discord.ext import commands
from modules import discord_voice
from modules.queue import queue
from modules.helper import embeds, config
from modules.commands import play


log = logging.getLogger(config.LOGGER_NAME)

class Play_Command(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @discord.app_commands.command(
        name="play", description="Play Music/Playlist from URL or name"
    )
    @discord.app_commands.describe(music_name="The URL or name of the Music/Playlist to play")
    async def play_command(self, interaction: discord.Interaction, music_name: str):
        await interaction.response.defer()
        ctx = await self.bot.get_context(interaction)
        await play.play(ctx, music_name)
    
    
    @play_command.autocomplete(name="music_name")
    async def play_autocomplete(
        self, interaction: discord.Interaction, music_name: str
    ):
        ctx = await self.bot.get_context(interaction)
        return await play.play_autocomplete(ctx, music_name)
        
    
# Resume command
class Resume(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @discord.app_commands.command(name="resume", description="Resume the current song")
    async def resume_command(self, interaction: discord.Interaction):
        await interaction.response.defer()
        ctx = await self.bot.get_context(interaction)
        await Resume.resume(ctx)
    
    async def resume(ctx: commands.Context):
        # Check if the bot is playing music
        if not queue.is_playing(ctx.guild.id):
            await ctx.send(embed=await embeds.no_music_playing())
            return
        
        # Get the current music and resume it
        music = queue.queue[ctx.guild.id].current_music
        
        music.voice_client.resume()
        await ctx.send(embed=await embeds.resumed_music(music, ctx))
    

# Pause command
class Pause(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @discord.app_commands.command(name="pause", description="Pause the current song")
    async def pause_command(self, interaction: discord.Interaction):
        await interaction.response.defer()
        ctx = await self.bot.get_context(interaction)
        await Pause.pause(ctx)
    
    
    async def pause(ctx: commands.Context):
        # Check if the bot is playing music
        if not queue.is_playing(ctx.guild.id):
            await ctx.send(embed=await embeds.no_music_playing())
            return
        
        # Get the current music and pause it
        music = queue.queue[ctx.guild.id].current_music
        
        music.voice_client.pause()
        await ctx.send(embed=await embeds.paused_music(music, ctx))


# Skip command
class Skip(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @discord.app_commands.command(name="skip", description="Skip the current song")
    async def skip_command(self, interaction: discord.Interaction):
        await interaction.response.defer()
        ctx = await self.bot.get_context(interaction)
        await Skip.skip(ctx)
    
    async def skip(ctx: commands.Context):
        # Check if the bot is playing music
        if not queue.is_playing(ctx.guild.id):
            await ctx.send(embed=await embeds.no_music_playing())
            return
        
        # Get the current music, stop and skip it
        music = queue.queue[ctx.guild.id].current_music
        
        discord_voice.stop_music(queue.queue[ctx.guild.id]) 
             
        await ctx.send(embed=await embeds.skipped_music(music, ctx))


# Clear command
class Clear(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @discord.app_commands.command(name="clear", description="Clear the music queue")
    async def clear_command(self, interaction: discord.Interaction):
        await interaction.response.defer()
        ctx = await self.bot.get_context(interaction)
        await Clear.clear(ctx)
    
    async def clear(ctx: commands.Context):
        # Check if the bot is playing music
        if queue.get_queue_length(ctx.guild.id) == 0:
            await ctx.send(embed=await embeds.no_music_playing())
            return

        # Clear the queue  
        queue.empty_queue(ctx.guild.id)  
        
        # If the bot is playing music, stop it
        if(queue.is_playing(ctx.guild.id) == True):
            queue.queue[ctx.guild.id].current_music
            discord_voice.stop_music(queue.queue[ctx.guild.id])
        
        await ctx.send(embed=await embeds.cleared_queue(ctx))


# Leave command
class Leave(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @discord.app_commands.command(name="leave", description="Leave the voice channel")
    async def leave_command(self, interaction: discord.Interaction):
        await interaction.response.defer()
        ctx = await self.bot.get_context(interaction)
        await Leave.leave(ctx)
    
    async def leave(ctx: commands.Context):        
        # Check if the bot is playing music, if so stop it and leave the channel
        
        # Clear the queue
        queue.empty_queue(ctx.guild.id)
        
        if(queue.is_playing(ctx.guild.id) == True):
            music = queue.queue[ctx.guild.id].current_music
            discord_voice.stop_music(queue.queue[ctx.guild.id])
            await music.voice_client.disconnect()
        # If the bot is not playing music, check if it is connected to a voice channel
        elif(ctx.guild.voice_client != None):
            await ctx.guild.voice_client.disconnect()

        await ctx.send(embed=await embeds.left_channel(ctx))


async def setup(bot: commands.Bot):
    await bot.add_cog(Play_Command(bot))
    await bot.add_cog(Resume(bot))
    await bot.add_cog(Pause(bot))
    await bot.add_cog(Skip(bot))
    await bot.add_cog(Clear(bot))
    await bot.add_cog(Leave(bot))