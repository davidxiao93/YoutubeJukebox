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
