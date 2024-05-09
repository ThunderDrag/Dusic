import discord
from discord import app_commands
import logging
from modules.search import spotify
from modules.queue import queue
from modules.helper import embeds
from modules.search import youtube
from modules.helper.class_types import Music


logger = logging.getLogger("Dusic")


# Play command to play music from URL or name
class Play:
    # Add the song to the queue
    async def play(interaction: discord.Interaction, music_name: str):
        await interaction.response.defer()

        logging.info(
            f"New play command from {interaction.user} with music name {music_name}"
        )

        # Create a music object
        music = Music()
        voice_channel = interaction.user.voice

        # If the user is not in a voice channel, send a message
        if voice_channel == None:
            await interaction.followup.send(
                "You need to be in a voice channel to play music"
            )
            return

        # If the user didn't provide a music name or URL then send a message
        if music_name == "":
            await interaction.followup.send("Please provide a music name or URL")
            return

        logging.info(f"Finding Music Type")
        # If the user has provided a URL, then check if its a valid URL and the type of music (playlist, album, track)
        music_name = await Play.find_music_type(music_name, music)

        logging.info(f"Searching for music on Spotify")
        # Search for the music
        results = await spotify.search(q=music_name, music_type=music.type)

        # If music was invalid, return
        if "error" in results:
            await interaction.followup.send(
                "Unable to find music. Please provide a valid music name or URL."
            )
            return

        # If the music is a search, get the first result
        if music.type == "search":
            results = results["tracks"]["items"][0]

        # Set music info
        music.set_data(
            name=results["name"],
            interaction=interaction,
            spotify_url=results["external_urls"]["spotify"],
        )

        # Set queue position
        queue_position = queue.get_queue_length(interaction.guild_id)

        # Images are at different part if its an track
        # If its a track, just add 1 to queue, if its playlist or album show a range of queue
        if music.type == "track" or music.type == "search":
            thumbnail = results["album"]["images"][0]["url"]
        else:
            thumbnail = results["images"][0]["url"]
            queue_position = f"{queue_position} - {int(queue_position) + len(results['tracks']['items'])}"

        music.set_data(thumbnail=thumbnail, queue_position=queue_position)

        await interaction.followup.send(embed=await embeds.added_to_queue(music))

        # Check if the guild exists in the queue, if it doesn't create a place
        queue.ensure_guild_in_queue(interaction.guild_id)

        # If its a track, just add the track to the queue
        if music.type == "track" or music.type == "search":
            music.set_data(
                name=results["name"],
                artist=results["artists"][0]["name"],
                duration_seconds=int(results["duration_ms"]) // 1000,
                interaction=interaction,
                spotify_url=results["external_urls"]["spotify"],
                voice_channel=voice_channel.channel,
                type="track",
            )

            music = youtube.find_music(music)
            await queue.add_music(interaction.guild_id, music)
        # If its a playlist or album, add all the tracks to the queue
        else:
            # Iterate over all the tracks in the playlist or album
            for track in results["tracks"]["items"]:
                music = Music()

                track = track["track"]

                music.set_data(
                    name=track["name"],
                    artist=track["artists"][0]["name"],
                    duration_seconds=int(track["duration_ms"]) // 1000,
                    interaction=interaction,
                    spotify_url=track["external_urls"]["spotify"],
                    voice_channel=voice_channel.channel,
                )

                music = youtube.find_music(music)
                await queue.add_music(interaction.guild_id, music)

                music = Music()

    # Play autocomplete to show results
    async def play_autocomplete(interaction: discord.Interaction, current: str):
        if current == "":
            return

        choices = []
        results = await spotify.search(q=current, music_type="search")

        for track in results["tracks"]["items"]:
            name = track["name"] + " - " + track["artists"][0]["name"]
            id = track["id"]
            choices.append(app_commands.Choice(name=name, value=id))

        return choices

    # Find the type of music (search because music name, playlist, album, track)
    async def find_music_type(music: str, music_info: Music):
        # If the user did not provide an url, track will be returned as its probably a music name
        music_type = "search"

        # If its an url, then determine the type and extract the ID from the URL
        if "spotify.com/playlist/" in music:
            music_type = "playlist"
            music = music.split("playlist/")[1]
        elif "spotify.com/album/" in music:
            music_type = "album"
            music = music.split("album/")[1]
        elif "spotify.com/track/" in music:
            music_type = "track"
            music = music.split("track/")[1]

        music_info.set_data(type=music_type)
        return music
