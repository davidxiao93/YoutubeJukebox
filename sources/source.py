from flask_socketio import SocketIO

from enums.download_status import DownloadStatus
from track import Track

class Source:

    def __init__(self, socketio: SocketIO):
        self.socketio = socketio

    def build_track(self, query: str) -> Track:
        return Track(
            source_id=query,
            title="Default Title",
            artist="Default Artist",
            thumbnail="Thumbnail url",
            length=100,
            download_status=DownloadStatus.QUEUED
        )

    def fetch_meta(self, track: Track) -> Track:
        """
        Fills in the Track based on the source_id
        """
        raise NotImplementedError


    def fetch_file(self, source_id: str) -> bool:
        """
        Attempts to download the file coresponding to the provided track
        :returns false if not successful
        """
        raise NotImplementedError
