import csv
import yt_dlp
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TIT2, TALB, TPE1
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def get_top_youtube_result(search_query):
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        search_url = f"https://www.youtube.com/results?search_query={search_query}"
        driver.get(search_url)

        # 一番上の動画のURLを取得
        video = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="video-title"]'))
        )
        url = video.get_attribute("href")

        return url
    finally:
        driver.quit()
        # 一回一回閉じるんじゃなくて開きつつ検索しつつで平行処理できれば早くなるのになーとか
        # めんどくさそうなので一旦これでおわり


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
            youtube_url = get_top_youtube_result(query)
            if youtube_url:
                print(f"Downloading: {row['Track Name']} by {row['Artist']}")
                download_video_as_mp3(youtube_url, output_dir, row["Track Name"])
                file_path = os.path.join(output_dir, f"{row['Track Name']}.mp3")
                add_metadata(file_path, row["Track Name"], row["Artist"], row["Album"])
                print(f"Metadata added for: {row['Track Name']}")


process_playlist("playlist.csv", "./downloads")
