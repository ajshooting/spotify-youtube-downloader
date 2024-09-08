import csv
import yt_dlp
from googleapiclient.discovery import build
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TIT2, TALB, TPE1
import os

YOUTUBE_API_KEY = "***"


def search_youtube(query):
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(q=query, part="snippet", maxResults=1)
    response = request.execute()

    if response["items"]:
        video_id = response["items"][0]["id"]["videoId"]
        return f"https://www.youtube.com/watch?v={video_id}"
    return None


def download_video_as_mp3(url, output_dir, track_name):
    output_path = os.path.join(output_dir, track_name)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,  # CSV内のタイトルをファイル名に使用
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "postprocessor_args": ["-ar", "44100"],
        "prefer_ffmpeg": True,
        "ffmpeg_location": "/usr/local/bin/ffmpeg",  # FFmpegの場所（必要に応じて変更）
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def add_metadata(file_path, title, artist, album):
    audio = EasyID3(file_path)
    audio["title"] = title
    audio["artist"] = artist
    audio["album"] = album
    audio.save()


def process_playlist(csv_file, output_dir):
    with open(csv_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            query = f"{row['Track Name']} {row['Artist']}"
            youtube_url = search_youtube(query)
            if youtube_url:
                print(f"Downloading: {row['Track Name']} by {row['Artist']}")
                download_video_as_mp3(youtube_url, output_dir, row["Track Name"])
                file_path = os.path.join(output_dir, f"{row['Track Name']}.mp3")
                add_metadata(file_path, row["Track Name"], row["Artist"], row["Album"])
                print(f"Metadata added for: {row['Track Name']}")


process_playlist("playlist.csv", "./downloads")
