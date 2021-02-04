from enum import Enum


class DownloadStatus(Enum):
    QUEUED = 0
    SEARCHING = 1
    DOWNLOADING = 2
    CAPTURED = 3
    ERROR = 4