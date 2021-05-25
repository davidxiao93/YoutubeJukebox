import os
from pathlib import Path

import youtube_dl
from youtubesearchpython import VideosSearch


from flask_socketio import SocketIO

from enums.download_status import DownloadStatus
from sources.source import Source
from track.track import Track

from functools import reduce



class YoutubeSource(Source):

    def __init__(self, socketio: SocketIO):
        super().__init__(socketio)

    def fetch_meta(self, track: Track) -> Track:
        query = track.source_id

        maybe_track = self.check_cache(query)
        if maybe_track is not None:
            track.source_id = maybe_track.source_id
            track.title = maybe_track.title
            track.artist = maybe_track.artist
            track.thumbnail = maybe_track.thumbnail
            track.duration = maybe_track.duration
            track.download_status = DownloadStatus.DOWNLOADING
            return track

        youtube_search = VideosSearch(query, limit=1)
        results = youtube_search.result()["result"]
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
            self.add_to_cache(query, track)
            return track
        raise Exception("Failed to search")


    def fetch_file(self, source_id: str) -> bool:
        """
        Returns True if the file is cached
        """
        my_file = Path("download/" + source_id + ".mp3")
        if my_file.is_file():
            return True

        temp_file = Path("download/temp")
        if temp_file.is_file():
            try:
                os.remove("download/temp")
            except:
                raise Exception("failed to delete temp file")

        youtube_id = source_id.replace("youtube_", "")

        ydl_opts = {
            # If there are any audio-only tracks, then youtube-dl will pick the best of them
            # Else, it will take the best track with video and audio
            'format': 'bestaudio/best',
            'outtmpl': 'download/temp',
            'quiet': True
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(['https://www.youtube.com/watch?v=' + youtube_id])

        return False

