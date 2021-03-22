from typing import Dict, Union, Optional

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

        # The fields below are not kept in cache
        self.download_status = download_status
        self.error: Optional[str] = None

    def build_state(self) -> Dict[str, Union[str, int]]:
        return {
            "source_id": self.source_id,
            "title": self.title,
            "artist": self.artist,
            "thumbnail_url": self.thumbnail,
            "duration": self.duration,
            "download_status": self.download_status.value,
            "error": "" if not self.error else self.error
        }
