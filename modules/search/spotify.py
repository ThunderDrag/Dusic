import aiohttp
import os
import logging
import modules.helper.config as config

# Setup the logger
log = logging.getLogger("Dusic")


# Setup the environment variables
# Token variable issued by Spotify every few hours
TOKEN = "la"

CLIENT_ID = config.SPOTIFY_CLIENT_ID
CLIENT_SECRET = config.SPOTIFY_CLIENT_SECRET


# Search for Music from name, or find track, playlist, album from url
async def search(q: str, music_type: str, limit="20"):
    global TOKEN, CLIENT_ID, CLIENT_SECRET

    # Query the API depending on the music type
    if music_type == "search":
        url = f"https://api.spotify.com/v1/search?q={q}&limit={limit}&offset=0&type=track"
    elif music_type == "playlist":
        url = f"https://api.spotify.com/v1/playlists/{q}"
    elif music_type == "album":
        url = f"https://api.spotify.com/v1/albums/{q}"
    elif music_type == "track":
        url = f"https://api.spotify.com/v1/tracks/{q}"

    headers = {"Authorization": f"Bearer {TOKEN}"}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            # If the status is not 200, refresh the token and try again
            if resp.status == 400 or resp.status == 401:
                log.error(f"Failed to search for {q} with status {resp.status}")
                log.info("Refreshing token")
                await get_token()
                return await search(q, music_type, limit)
            elif resp.status == 404:
                return {"error": "Unable to find music"}

            return await resp.json()


# Refreshes auth token for spotify
async def get_token():
    global TOKEN
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as resp:
            TOKEN = (await resp.json())["access_token"]
