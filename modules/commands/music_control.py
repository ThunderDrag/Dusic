import discord
from discord.ext import commands
from discord import app_commands
import logging
from modules.queue import queue
from modules.discord_voice import Play_On_Discord
from modules.commands.play import Play

logger = logging.getLogger("Dusic")


class Play(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="play", description="Play Music/Playlist from URL or name"
    )
    @app_commands.describe(music_name="The URL or name of the Music/Playlist to play")
    async def play_command(self, interaction: discord.Interaction, music_name: str):
        await Play.play_command(interaction, music_name)

    @play_command.autocomplete("music_name")
    async def play_command_autocomplete(
        self, interaction: discord.Interaction, current: str
    ):
        return await Play.play_command_autocomplete(interaction, current)


class Resume(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="resume", description="Resume the currently playing music"
    )
    async def resume_command(self, interaction: discord.Interaction):
        await Resume.resume(interaction)

    async def resume(self, interaction: discord.Interaction):
        await interaction.response.defer()

        logging.info(f"New resume command from {interaction.user}")

        guildID = interaction.guild_id

        # If the bot is not playing music, send a message
        if not queue.is_playing(guildID):
            await interaction.followup.send("No music is playing")
            return

        # Get the voice client
        voice_client = queue.queue[guildID].currently_playing.voice_client

        # Resume the music
        if voice_client.is_paused() == False:
            await interaction.followup.send("Music is already playing")
            return

        voice_client.resume()

        await interaction.followup.send(
            f"Resumed song: '{queue.queue[guildID].currently_playing.name}'"
        )


class Pause(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="pause", description="Pause the currently playing music")
    async def pause_command(self, interaction: discord.Interaction):
        await self.pause(interaction)

    async def pause(self, interaction: discord.Interaction):
        await interaction.response.defer()

        logging.info(f"New pause command from {interaction.user}")

        guildID = interaction.guild_id

        # If the bot is not playing music, send a message
        if not queue.is_playing(guildID):
            await interaction.followup.send("No music is playing")
            return

        # Get the voice client
        voice_client = queue.queue[guildID].currently_playing.voice_client

        # Pause the music
        voice_client.pause()

        await interaction.followup.send(
            f"Paused song: '{queue.queue[guildID].currently_playing.name}'"
        )


class Skip(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="skip", description="Skip the currently playing music")
    async def skip_command(self, interaction: discord.Interaction):
        await self.skip(interaction)

    async def skip(self, interaction: discord.Interaction):
        await interaction.response.defer()

        logging.info(f"New skip command from {interaction.user}")

        guildID = interaction.guild_id
        music = queue.queue[guildID].currently_playing

        # If the bot is not playing music, send a message
        if not queue.is_playing(guildID):
            await interaction.followup.send("No music is playing")

        Play_On_Discord.stop_music(music, queue.queue[guildID])

        await interaction.followup.send(f"Skipped song: '{music.name}'")


class Clear(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="clear", description="Clear the queue")
    async def clear_command(self, interaction: discord.Interaction):
        await self.clear(interaction)

    async def clear(self, interaction: discord.Interaction):
        await interaction.response.defer()

        logging.info(f"New clear command from {interaction.user}")

        guildID = interaction.guild_id
        music = queue.queue[guildID].currently_playing

        # If the bot is not playing music, send a message
        if queue.get_queue_length(guildID) == 0:
            await interaction.followup.send("No music in queue")
            return

        if queue.queue[guildID].currently_playing is not None:
            Play_On_Discord.stop_music(music, queue.queue[guildID], True)

        # Clear the queue
        queue.queue[guildID].music = []

        await interaction.followup.send("Cleared the queue")


async def setup(bot: commands.Bot):
    await bot.add_cog(Play(bot))
    await bot.add_cog(Resume(bot))
    await bot.add_cog(Pause(bot))
    await bot.add_cog(Skip(bot))
    await bot.add_cog(Clear(bot))
