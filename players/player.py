import time
from typing import Dict, Union, Optional

from flask_socketio import SocketIO

from track import Track

import threading

class Player(threading.Thread):

    def __init__(self, socketio: SocketIO):
        super().__init__()
        self.process = None
        self.socketio = socketio
        self.current_track: Optional[Track] = None
        self.current_track_started = 0

        # This class will handle volume control
        self.current_volume = 0
        self.volume_muted = False

    def build_state(self) -> Dict[str, Union[str, int, Dict[str, Union[str, int]]]]:
        if self.current_track is None:
            return {
                "current_track": {},
                "started": 0,
                "is_playing": False,
                "volume": self.get_volume(),
                "is_muted": self.is_muted()
            }
        return {
            "current_track": self.current_track.build_state(),
            "started": self.current_track_started, # unix timestamp in seconds
            "is_playing": self.is_playing(),
            "volume": self.get_volume(),
            "is_muted": self.is_muted()
        }

    def get_volume(self) -> int:
        return self.current_volume

    def is_muted(self) -> bool:
        return self.volume_muted

    def vol_increase(self):
        self.current_volume += 10
        if self.current_volume > 100:
            self.current_volume = 100
        # TODO: set volume
        self.push_now_playing_state()

    def vol_decrease(self):
        self.current_volume -= 10
        if self.current_volume < 0:
            self.current_volume = 0
        # TODO: set volume
        self.push_now_playing_state()

    def vol_mute_toggle(self):
        self.volume_muted = not self.volume_muted
        # TODO: set volume muted status
        self.push_now_playing_state()

    def push_now_playing_state(self):
        self.socketio.emit("now_playing", self.build_state())

    def play_next(self, track: Optional[Track]):
        self.current_track = track
        self.stop_playing()
        if self.current_track is not None:
            self.start_playing()

    def start_playing(self):
        raise NotImplementedError

    def stop_playing(self):
        raise NotImplementedError

    def is_playing(self) -> bool:
        raise NotImplementedError

    def is_finished(self) -> bool:
        raise NotImplementedError


