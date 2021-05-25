from typing import Dict, Union, Optional

from enums.download_status import DownloadStatus
from track.track_info import TrackInfo


class Track:
    def __init__(self, query: str):
        self.query: str = query
        self.info: Optional[TrackInfo] = None
        self.download_status = DownloadStatus.QUEUED
        self.error: Optional[str] = None

    def build_state(self, is_favourite: bool) -> Dict[str, Union[str, int]]:
        return {
            "info": None if not self.info else self.info.build_state(),
            "is_favourite": is_favourite,
            "download_status": self.download_status.value,
            "error": "" if not self.error else self.error
        }
