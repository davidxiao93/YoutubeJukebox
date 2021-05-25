import csv
from collections import OrderedDict
from socket import SocketIO
from typing import List, Dict, Union

from track.track import Track
from track.track_info import TrackInfo

FAVOURITES_FILE = "favourites.csv"
TRACK_FIELDS = ["source_id", "title", "artist", "thumbnail", "duration"]


class Favourites:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.favourites: Dict[str, TrackInfo] = OrderedDict()
        try:
            with open(FAVOURITES_FILE) as favourites_file:
                reader = csv.DictReader(favourites_file, fieldnames=TRACK_FIELDS)
                for row in reader:
                    self.favourites[row["source_id"]] = TrackInfo(
                        row["source_id"],
                        row["title"],
                        row["artist"],
                        row["thumbnail"],
                        int(row["duration"])
                    )
        except FileNotFoundError as e:
            # Expected error if starting server from scratch, will be self handed when the file is created
            pass
        except:
            raise Exception("Failed to load favourites file")

    def build_state(self) -> Dict[str, List[Dict[str, Union[str, int]]]]:
        return {
            "favourites": [
                track_info.build_state()
                for track_info in self.favourites.values()
            ]
        }

    def push_favourites_state(self):
        self.socketio.emit("favourites", self.build_state())

    def is_favourite(self, track: Track) -> bool:
        return track.info and track.info.source_id in self.favourites

    def add_favourite(self, track_info: TrackInfo):
        if track_info.source_id not in self.favourites:
            self.favourites[track_info.source_id] = track_info
            self.update_repo()
            self.push_favourites_state()

    def remove_favourite(self, track_info: TrackInfo):
        self.delete_favourite(track_info.source_id)

    def delete_favourite(self, source_id: str):
        if source_id in self.favourites:
            self.favourites.pop(source_id)
            self.update_repo()
            self.push_favourites_state()

    def update_repo(self):
        try:
            # Using 'w' mode to overwrite it. This does not need to be performant
            with open(FAVOURITES_FILE, 'w') as favourites_file:
                writer = csv.DictWriter(favourites_file, fieldnames=TRACK_FIELDS)
                for favourite_track_info in self.favourites.values():
                    writer.writerow({
                        "source_id": favourite_track_info.source_id,
                        "title": favourite_track_info.title,
                        "artist": favourite_track_info.artist,
                        "thumbnail": favourite_track_info.thumbnail,
                        "duration": favourite_track_info.duration
                    })
        except:
            raise Exception("Failed to update favourites file")


