from dotenv import load_dotenv
import os

load_dotenv()

# Discord Bot Token
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Spotify API
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Opus Path
OPUS_PATH = os.getenv("OPUS_PATH")

# OPENAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Music Folder
MUSIC_FOLDER = "music/"

# Number of download processes
DOWNLOAD_PROCESSES = 3
