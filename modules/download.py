import os
import logging
import multiprocessing
import pytube
import asyncio
import modules.helper.config as config
from modules.helper.types import Music


# Create a logger
logger = logging.getLogger(config.LOGGER_NAME)

# Get all the music files in the music folder, the key is the yt_id and the value is the file name with extension
music_files = [file for file in os.listdir(config.MUSIC_FOLDER)]

# Initialize the results, download queue, and processes list
download_queue = multiprocessing.Queue()
results = None
processes = []


# Ensure that the music is downloaded, if not then download it
async def ensure_music_is_downloaded(music: Music):
    youtube_url = music.youtube_url
    youtube_id = music.youtube_id
    

    logger.info(f"Checking if music is downloaded for {music.name}")

    # If the music is already downloaded, then return
    if youtube_id in music_files:
        music.set_data(file_path=config.MUSIC_FOLDER + youtube_id)
        return

    # We change it to downloading so that we don't download it again from queue
    music.set_data(file_path="downloading")

    # Add the music to the download queue
    download_queue.put({"youtube_url": youtube_url, "file_name": youtube_id})

    # Wait for the music to be downloaded
    while youtube_url not in results.keys():
        await asyncio.sleep(0.1)

    # Set the file name
    music.set_data(file_path=results[youtube_url])
    
    results.pop(youtube_url)

    # Add the music to the music files
    music_files.append(youtube_id)


# Download the music
def downloader(download_queue: multiprocessing.Queue, results: dict):
    while True:
        # Get the music from the download queue, if there is no music then continue
        try:
            data = download_queue.get(timeout=5)
        except:
            continue
        
        youtube_url = data["youtube_url"]
        file_name = data["file_name"]
        
        logger.info(f"Downloading music from {youtube_url}")

        youtube = pytube.YouTube(youtube_url)

        # Filter the streams, get the best audio stream, and download it
        file = (
            youtube.streams.filter(only_audio=True)
            .order_by("abr")
            .desc()
            .first()
            .download(config.MUSIC_FOLDER, filename=file_name)
        )

        results[youtube_url] = file


# Initialize the download queue
def initalize_download_queue():
    global results

    # Create manager, results dictionary
    manager = multiprocessing.Manager()
    results = manager.dict()

    # Start N processes for downloading music
    for _ in range(config.DOWNLOAD_PROCESSES):
        p = multiprocessing.Process(target=downloader, args=(download_queue, results))
        p.start()
        processes.append(p)


# Terminate all the processes
def terminate_processes():
    for p in processes:
        p.terminate()
        logger.info(f"Terminated process {p.pid}")

        download_queue.close()
