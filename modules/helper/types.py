import discord
from discord.ext import commands
from typing import List



class Music:    
    # Music Attributes
    name: str = None
    artist: str = None
    duration_seconds: int = None
    thumbnail_url: str = None
    music_type: str = None
    
    # Spotify Attributes
    spotify_url: str = None
    
    # YouTube Attributes
    youtube_url: str = None
    youtube_id: str = None
    
    # Discord Attributes
    context: commands.Context = None
    voice_channel: discord.VoiceChannel = None
    voice_client: discord.VoiceClient = None
    ffmpeg_process: discord.FFmpegPCMAudio = None
    position: int = 0,
    voice_channel_changing: bool = False
    
    # File Attributes
    file_path: str = None

    def __init__(self):
        pass

    def set_data(self,
    name: str = None,
    artist: str = None,
    duration_seconds: int = None,
    thumbnail_url: str = None,
    music_type: str = None,
    
    # Spotify Attributes
    spotify_url: str = None,
    
    # YouTube Attributes
    youtube_url: str = None,
    youtube_id: str = None,
    
    # Discord Attributes
    context: commands.Context = None,
    voice_channel: discord.VoiceChannel = None,
    voice_client: discord.VoiceClient = None,
    ffmpeg_process: discord.FFmpegPCMAudio = None,
    position: int = 0,
    voice_channel_changing: bool = False,
    
    # File Attributes
    file_path: str = None
    ):
    
        
        
        for key, value in locals().items():
            if key != "self" and value != None:
                setattr(self, key, value)


class GuildQueue:
    music: List[Music] = []
    current_music: Music = None
    afk_timer: int = None
    
    def __init__(self):
        pass
    