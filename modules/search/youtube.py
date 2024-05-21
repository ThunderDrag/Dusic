import ytmusicapi
from modules.helper.types import Music


# Search the song on youtube, find the best match then return it
def find_music(music: Music, limit=5):
    # Create a ytmusic object and search for the music
    ytmusic = ytmusicapi.YTMusic()
    # Search for the music with the title and artist
    search_results = ytmusic.search(music.name + " " + music.artist, limit=limit)

    # Find the best match for the music and add the url and thumbnail
    best_match = find_best_match(music, search_results, limit)
    
    if not best_match:
        return False

    music.set_data(
        youtube_id=best_match["videoId"],
        youtube_url="https://music.youtube.com/watch?v=" + best_match["videoId"]
    )

    return music


# Find the best match for the music using several factors
def find_best_match(music: Music, search_results: list, limit):
    # First, remove all the results that don't have the duration tag
    search_results = [x for x in search_results if "duration_seconds" in x]
    top_result = search_results[0]
    
    
    # If the top result has almost the same duration as the music, then return it
    if(abs(top_result["duration_seconds"] - music.duration_seconds) <= 10):
        return top_result
    
    # If the top result doesn't match, then we try and check Song results
    for result in search_results:
        if(result["category"] != "Songs"):
            continue
        
        if abs(result["duration_seconds"] - music.duration_seconds) <= 10:
            return result


    # If no result has the same duration, then we return the first result that has videoId  
    for result in search_results:
        if "videoId" in result:
            return result

    
    
    # If no result has the same duration, then we search again with a limit of 50
    # If the limit is already 50, then we return the first result
    if limit == 50:
        return False

    return find_music(music, 50)
