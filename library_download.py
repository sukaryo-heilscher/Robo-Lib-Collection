import sys
import os
import re
import subprocess
from pytube import Playlist, YouTube

def extract_date(title):
    # Extract the date from the title if present
    match = re.search(r'\[(\d{2}/\d{2}/\d{4})\]', title)
    if match:
        # Replace '/' with '_' in the date
        return match.group(1).replace('/', '_')
    else:
        return None

def download_audio(youtube_url):
    output_path = "./lib_audio/"
    output_format = "mp3"

    try:
        # Create a YouTube object
        yt = YouTube(youtube_url)

        # Extract the date from the title
        date = extract_date(yt.title)
        if date:
            # Define output file path
            output_file_path = os.path.join(output_path, f"{date}_library.{output_format}")

            # Download audio using yt-dlp
            command = f'yt-dlp --extract-audio --audio-format {output_format} --audio-quality 124k --output "{output_file_path}" {youtube_url}'
            subprocess.run(command, shell=True, check=True)

            print(f"Audio downloaded successfully as {output_format} format!")
        else:
            print(f"No date found in the video title for {youtube_url}. Skipping.")
    except Exception as e:
        print(f"Error downloading audio: {e}")

def download_audio_from_playlist(playlist_url):
    try:
        # Create a Playlist object
        playlist = Playlist(playlist_url)

        # Iterate over each video in the playlist
        for video_url in playlist.video_urls:
            download_audio(video_url)
    except Exception as e:
        print(f"Error downloading playlist: {e}")

# Example usage
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_audio.py <YouTube_URL>")
        print("Usage: python download_audio.py <Playlist_URL>")
        sys.exit(1)

    url = sys.argv[1]

    if "playlist?list=" in url:
        download_audio_from_playlist(url)
    else:
        download_audio(url)
