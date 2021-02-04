from typing import Dict, Union

from enums.download_status import DownloadStatus


class Track:
    def __init__(self,
                 source_id: str,
                 title: str,
                 artist: str,
                 thumbnail: str,
                 length: int,
                 download_status: DownloadStatus):
        self.source_id = source_id
        self.title = title
        self.artist = artist
        self.thumbnail = thumbnail
        self.length = length
        self.download_status = download_status

    def build_state(self) -> Dict[str, Union[str, int]]:
        return {
            "source_id": self.source_id,
            "title": self.title,
            "artist": self.artist,
            "thumbnail_url": self.thumbnail,
            "length": self.length,
            "download_status": self.download_status.name
        }