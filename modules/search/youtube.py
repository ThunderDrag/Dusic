import ytmusicapi
from modules.helper.class_types import Music


# Search the song on youtube, find the best match then return it
def find_music(music: Music, limit=5):
    # Create a ytmusic object and search for the music
    ytmusic = ytmusicapi.YTMusic()
    # Search for the music with the title and artist
    search_results = ytmusic.search(music.name + " " + music.artist, limit=limit)

    # Find the best match for the music and add the url and thumbnail
    best_match = find_best_match(music, search_results, limit)

    music.set_data(
        yt_id=best_match["videoId"],
        yt_url="https://music.youtube.com/watch?v=" + best_match["videoId"],
        thumbnail=best_match["thumbnails"][-1]["url"],
    )

    return music


# Find the best match for the music using several factors
def find_best_match(music: Music, search_results: list, limit):
    # First, remove all the results that don't have the duration tag
    search_results = [x for x in search_results if "duration_seconds" in x]

    # Then, we iterate over the search results and check, if the duration of the search result is within 10 seconds of the music
    # Then we return it, else we just return the top result
    for result in search_results:
        if result["duration_seconds"] - music.duration_seconds <= 20:
            return result

    # Check if the result has videoId, if it does then return it else return the next result that has it
    for result in search_results:
        if "videoId" in result:
            return result

    # If no result has videoId, then search again with limit of 20, if limit is already 20 then search with 50
    if limit == 20:
        return find_music(music, 50)

    return find_music(music, 20)
