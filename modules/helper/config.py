from dotenv import load_dotenv
import os

load_dotenv()

# Logger Name
LOGGER_NAME = "dusic"

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


# Time allowed before bot is kicked for AFK
AFK_TIME = 600


# Webhook URL for error logging
WEBHOOK_URL = "https://discord.com/api/webhooks/1239499156301811754/Qlri9qqkEV73HRVCf-F4eJokhwOyErGMGEdbEJX7kpprtDgs-Tl2E2icQ_cSqFflOAMB"
