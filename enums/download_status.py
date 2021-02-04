from enum import Enum


class DownloadStatus(Enum):
    QUEUED = 0
    DOWNLOADING = 1
    CAPTURED = 2
    ERROR = 3