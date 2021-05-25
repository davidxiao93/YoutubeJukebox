from typing import Dict, Union


class TrackInfo:
    def __init__(self,
                 source_id: str,
                 title: str,
                 artist: str,
                 thumbnail: str,
                 duration: int):
        self.source_id = source_id
        self.title = title
        self.artist = artist
        self.thumbnail = thumbnail
        self.duration = duration # in seconds

    def build_state(self) -> Dict[str, Union[str, int]]:
        return {
            "source_id": self.source_id,
            "title": self.title,
            "artist": self.artist,
            "thumbnail_url": self.thumbnail,
            "duration": self.duration
        }
