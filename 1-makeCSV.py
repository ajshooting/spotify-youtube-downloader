import spotipy
from spotipy.oauth2 import SpotifyOAuth
import csv

# Spotifyの認証情報
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id="***",
        client_secret="***",
        redirect_uri="https://www.google.com/",
        scope="playlist-read-private",
    )
)


def export_playlist_to_csv(playlist_id, output_file):
    results = sp.playlist_tracks(playlist_id, limit=100)
    tracks = results["items"]

    # ページネーションで全てのトラックを取得
    while results["next"]:
        results = sp.next(results)
        tracks.extend(results["items"])

    # CSVファイルに書き込み
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Track Name", "Artist", "Album", "ISRC"])

        for item in tracks:
            track = item["track"]
            name = track["name"]
            artist = track["artists"][0]["name"]
            album = track["album"]["name"]
            isrc = track["external_ids"].get("isrc", "")
            writer.writerow([name, artist, album, isrc])


export_playlist_to_csv("playlist_id", "playlist.csv")
