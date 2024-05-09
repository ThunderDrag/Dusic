import discord
from discord.ext import commands
from typing import List


class Music:
    name: str
    artist: str
    interaction: discord.Interaction
    duration_seconds: int
    type: str
    spotify_url: str
    thumbnail: str
    queue_position: str
    yt_id: str
    yt_url: str
    voice_channel: discord.VoiceChannel
    voice_client: discord.VoiceClient
    ffmpeg_process: discord.FFmpegPCMAudio
    file_name: str

    def __init__(self):
        self.name = None
        self.artist = None
        self.interaction = None
        self.duration_seconds = None
        self.type = None
        self.spotify_url = None
        self.thumbnail = None
        self.queue_position = None
        self.yt_id = None
        self.yt_url = None
        self.voice_channel = None
        self.voice_client = None
        self.ffmpeg_process = None
        self.file_name = None

    def set_data(
        self,
        name: str = None,
        artist: str = None,
        interaction: discord.Interaction = None,
        duration_seconds: int = None,
        type: str = None,
        spotify_url: str = None,
        thumbnail: str = None,
        queue_position: str = None,
        yt_id: str = None,
        yt_url: str = None,
        voice_channel: discord.VoiceChannel = None,
        voice_client: discord.VoiceClient = None,
        ffmpeg_process: discord.FFmpegPCMAudio = None,
        file_name: str = None,
    ):
        for key, value in locals().items():
            if key != "self" and value != None:
                setattr(self, key, value)


class GuildQueue:
    music: List[Music]
    currently_playing: Music | None

    def __init__(self) -> None:
        self.music = []
        self.currently_playing = None


class MimicInteraction:
    class Response:
        async def defer(self):
            pass

    class Followup:
        async def send(self, message):
            pass

    context: commands.Context
    user: discord.User
    response: Response
    followup: Followup

    def __init__(self, context: commands.Context) -> None:
        self.context = context
        self.user = context.author
        self.response = self.Response()
        self.followup = self.Followup()
