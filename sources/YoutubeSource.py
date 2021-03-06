from pathlib import Path

import youtube_dl
from youtubesearchpython import VideosSearch


from flask_socketio import SocketIO

from enums.download_status import DownloadStatus
from sources.source import Source
from track import Track

from functools import reduce



class YoutubeSource(Source):

    def __init__(self, socketio: SocketIO):
        super().__init__(socketio)

    def fetch_meta(self, track: Track) -> Track:
        videosSearch = VideosSearch(track.source_id, limit=1)
        results = videosSearch.result()["result"]
        if len(results) == 0:
            raise Exception("No results")
        result = results[0]
        if isinstance(result, dict):
            track.source_id = "youtube_" + result["id"]
            track.title = result["title"]
            track.artist = result["channel"]["name"]
            track.thumbnail = max(result["thumbnails"], key=lambda t: t["width"] * t["height"])["url"]
            track.duration = reduce(
                lambda a, b: 60 * a + b,
                [int(x) for x in result["duration"].split(":")],
                0
            )
            track.download_status = DownloadStatus.DOWNLOADING
            return track
        raise Exception("Failed to search")


    def fetch_file(self, source_id: str):
        my_file = Path("download/" + source_id + ".mp3")
        if my_file.is_file():
            return True

        youtube_id = source_id.replace("youtube_", "")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'download/youtube_%(id)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'postprocessor_args': [
                # Apply loudness normalisation
                '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
                # Trim silence
                '-af', 'silenceremove=start_periods=1:start_duration=1:start_threshold=-60dB:detection=peak,aformat=dblp,areverse,silenceremove=start_periods=1:start_duration=1:start_threshold=-60dB:detection=peak,aformat=dblp,areverse'
            ]
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(['https://www.youtube.com/watch?v=' + youtube_id])


