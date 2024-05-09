import os
import modules.helper.config as config
from modules.helper.class_types import Music
import logging
import multiprocessing
import pytube
import asyncio


# Create a logger
logger = logging.getLogger("Dusic")

# Get all the music files in the music folder, the key is the yt_id and the value is the file name with extension
music_files = {file.split(".")[0]: file for file in os.listdir(config.MUSIC_FOLDER)}

# Initialize the results, download queue, and processes list
download_queue = multiprocessing.Queue()
results = None
processes = []


# Ensure that the music is downloaded, if not then download it
async def ensure_music_is_downloaded(music: Music):
    file_name = music.file_name

    logger.info(f"Checking if music is downloaded for {music.name}")

    # Check if the file name is not None
    if file_name != None:
        return

    # We change it to downloading so that we don't download it again from queue
    music.file_name = "downloading"

    # Check if the file exists in the music folder, if it does then set the file name
    if music.yt_id in music_files:
        music.file_name = music_files[music.yt_id]
        return

    # Add the music to the download queue
    download_queue.put({"yt_url": music.yt_url, "file_name": music.yt_id})

    # Wait for the music to be downloaded
    while music.yt_url not in results.keys():
        await asyncio.sleep(0.1)

    # Set the file name
    music.file_name = music.yt_id
    results.pop(music.yt_url)

    # Add the music to the music files
    music_files[music.yt_id] = music.file_name


# Download the music
def downloader(download_queue: multiprocessing.Queue, results: dict):
    while True:
        # Get the music from the download queue, if there is no music then continue
        try:
            data = download_queue.get(timeout=5)
        except:
            continue

        logger.info(f"Downloading music from {data["yt_url"]}")

        youtube = pytube.YouTube(data["yt_url"])

        # Download the music
        file = (
            youtube.streams.filter(only_audio=True)
            .order_by("abr")
            .desc()
            .first()
            .download(config.MUSIC_FOLDER, filename=data["file_name"])
        )

        results[data["yt_url"]] = file


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
