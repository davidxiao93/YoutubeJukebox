from enum import Enum


class DownloadStatus(Enum):
    QUEUED = 0
    SEARCHING = 1
    DOWNLOADING = 2
    PROCESSING = 3
    CAPTURED = 4
    ERROR = 5