import discord
import logging
import asyncio
from discord.ext import commands
from modules.queue import queue
from modules.search import spotify, youtube
from modules.helper import embeds, logger, config
from modules.helper.types import Music


log = logging.getLogger(config.LOGGER_NAME)


async def play(ctx: commands.Context, music_name: str):
    log.info("Recieved play command for: " + music_name)

    # If the user is not in a voice channel, return
    if ctx.author.voice is None:
        await ctx.reply("You are not in a voice channel.", ephemeral=True)
        return

    # If the user did not provide a music name, return
    if music_name == "":
        await ctx.reply("Please provide a music name or URL.", ephemeral=True)
    
    
    # Create music
    music = Music()
    
    # Find the music type
    music = find_music_type(music, music_name)
    log.info("Searching for music on Spotify")
    results = await spotify.search(q=music.name, music_type=music.music_type)
    
    # If no results were found, return
    # If the music type is a track and there is an error in the results, or if the music type is not a track and the total tracks are 0
    if (music.music_type == "track" and "error" in results) or (music.music_type != "track" and results["tracks"]["total"] == 0):
        await ctx.reply("No results found for: ```" + music.name + "``` on Spotify. Try new music name or providing direct Spotify URL", ephemeral=True)
        return
    
    # If the music type is a search query, then get the first result
    if music.music_type == "search":
        music.music_type = "track"
        results = results["tracks"]["items"][0]

    
    # Send embed
    await send_embed(ctx, music, results)
    
    # If the music type is a playlist, then add all the tracks to the queue
    if music.music_type == "track":
        await add_to_queue(ctx, music, results)
    else:
        for track in results["tracks"]["items"]:
            music = Music()
            track = track["track"]
            await add_to_queue(ctx, music, track)
            
            # Wait for 1 second so that the bot can do other things meanwhile
            await asyncio.sleep(1)
    
    

# Find the music type, like is it a playlist, track, album url or a search query
def find_music_type(music: Music, music_name: str):
    music_type = "search"
    
    # If its an url, then determine the type and extract the ID from the URL
    if "spotify.com/playlist/" in music_name:
        music_type = "playlist"
        music_name = music_name.split("playlist/")[1]
    elif "spotify.com/album/" in music_name:
        music_type = "album"
        music_name = music_name.split("album/")[1]
    elif "spotify.com/track/" in music_name:
        music_type = "track"
        music_name = music_name.split("track/")[1]
    
    music.set_data(
        name=music_name,
        music_type=music_type    
    )
    
    return music


# Extract data and send embed
async def send_embed(ctx: commands.Context, music: Music, spotify_result: dict):
    name = spotify_result["name"]
    spotify_url = spotify_result["external_urls"]["spotify"]
    queue_position = queue.get_queue_length(ctx.guild.id)
    
    if music.music_type == "track":
        thumbnail = spotify_result["album"]["images"][0]["url"]
    else:
        thumbnail = spotify_result["images"][0]["url"]
        queue_position = f"{queue_position} - {int(queue_position) + len(spotify_result['tracks']['items'])}"
    
    await ctx.reply(embed=await embeds.added_to_queue(name, spotify_url, queue_position, ctx.author.id, thumbnail))

    
# Search on youtube and then add music to the queue
async def add_to_queue(ctx: commands.Context, music: Music, spotify_result: dict):
    music.set_data(
        name=spotify_result["name"],
        artist=spotify_result["artists"][0]["name"],
        duration_seconds=spotify_result["duration_ms"] / 1000,
        thumbnail_url=spotify_result["album"]["images"][0]["url"],

        spotify_url="https://open.spotify.com/track/" + spotify_result["id"],
        
        context=ctx,
        voice_channel=ctx.author.voice.channel,
    )
    
    result = youtube.find_music(music)
    
    if not result:
        await ctx.reply("No results found for: " + music.name + "on YouTube", ephemeral=True)
        return
    
    await queue.add_music(ctx.guild.id, music)
    

async def play_autocomplete(ctx: commands.Context, music_name: str):
    if music_name == "":
        return

    choices = []
    results = await spotify.search(q=music_name, music_type="search")

    for track in results["tracks"]["items"]:
        name = track["name"] + " - " + track["artists"][0]["name"]
        id = "spotify.com/track/" + track["id"]
        choices.append(discord.app_commands.Choice(name=name, value=id))

    return choices