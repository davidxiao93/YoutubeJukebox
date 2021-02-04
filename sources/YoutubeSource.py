
"""
Need to look into how to embed youtube dl too
https://github.com/ytdl-org/youtube-dl/blob/master/README.md#embedding-youtube-dl
"""

import youtube_dl
from flask_socketio import SocketIO

from enums.download_status import DownloadStatus
from sources.source import Source
from track import Track


class YoutubeSource(Source):

    def __init__(self, socketio: SocketIO):
        super().__init__(socketio)

    def fetch_meta(self, track: Track) -> Track:
        self.socketio.sleep(2)
        return track

    def fetch_file(self, query: str) -> bool:
        """
        Attempts to download the file coresponding to the provided track
        :returns false if not successful

                future additions
                    - downloads only audio
                    - have a mp3 cache (limit cache size though)
                    - normalise the mp3
        """
        self.socketio.sleep(10)
        return True
