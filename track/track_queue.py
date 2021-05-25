from typing import List, Dict, Optional, Union

from flask_socketio import SocketIO

from enums.download_status import DownloadStatus
from favourites.favourites import Favourites
from track.track import Track


class TrackQueue:
    def __init__(self, socketio: SocketIO, favourites: Favourites):
        self.socketio = socketio
        self.favourites = favourites
        self.queue: List[Track] = []

    def build_state(self) -> Dict[str, List[Dict[str, Union[str, int]]]]:
        return {
            "queue": [
                track.build_state(
                    is_favourite=self.favourites.is_favourite(track)
                )
                for track in self.queue
            ]
        }

    def push_queue_state(self):
        self.socketio.emit("queue", self.build_state())

    def get_next_track(self) -> Optional[Track]:
        if len(self.queue) == 0:
            return None
        next_track = self.queue.pop(0)
        while len(self.queue) != 0 and next_track.download_status == DownloadStatus.ERROR:
            next_track = self.queue.pop(0)
        self.push_queue_state()
        if next_track.download_status != DownloadStatus.CAPTURED:
            return None
        return next_track

    def add_track(self, track: Track):
        self.queue.append(track)
        self.push_queue_state()

    def remove_track(self, index: int):
        if 0 <= index < len(self.queue):
            self.queue.pop(index)
            self.push_queue_state()

    def get_track_at(self, index: int) -> Optional[Track]:
        if 0 <= index < len(self.queue):
            return self.queue[index]
        return None

    def clear_queue(self):
        self.queue = []
        self.push_queue_state()

    def raise_track(self, index: int):
        if 1 <= index < len(self.queue):
            self._switch_track(index - 1, index)

    def lower_track(self, index: int):
        if 0 <= index < len(self.queue) - 1:
            self._switch_track(index, index + 1)

    def _switch_track(self, a: int, b: int):
        t = self.queue[a]
        self.queue[a] = self.queue[b]
        self.queue[b] = t
        self.push_queue_state()