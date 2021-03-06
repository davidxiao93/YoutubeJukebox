from typing import Dict, Union

from enums.download_status import DownloadStatus


class Track:
    def __init__(self,
                 source_id: str,
                 title: str,
                 artist: str,
                 thumbnail: str,
                 duration: int,
                 download_status: DownloadStatus):
        self.source_id = source_id
        self.title = title
        self.artist = artist
        self.thumbnail = thumbnail
        self.duration = duration # in seconds
        self.download_status = download_status

    def build_state(self) -> Dict[str, Union[str, int]]:
        return {
            "source_id": self.source_id,
            "title": self.title,
            "artist": self.artist,
            "thumbnail_url": self.thumbnail,
            "duration": self.duration,
            "download_status": self.download_status.name
        }