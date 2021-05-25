from enums.download_status import DownloadStatus
from track.track import Track
from track.track_info import TrackInfo


def track_to_track_info(track: Track) -> TrackInfo:
    return TrackInfo(
        track.source_id,
        track.title,
        track.artist,
        track.thumbnail,
        track.duration
    )


def track_info_to_track(track_info: TrackInfo) -> Track:
    return Track(
        track_info.source_id,
        track_info.title,
        track_info.artist,
        track_info.thumbnail,
        track_info.duration,
        DownloadStatus.QUEUED
    )