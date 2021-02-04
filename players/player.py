import time
from typing import Dict, Union, Optional

from track import Track


class Player:

    current_track: Optional[Track] = None

    def build_state(self) -> Dict[str, Union[str, int, Dict[str, Union[str, int]]]]:
        return {
            "current_track": self.current_track.build_state() if self.current_track is not None else {},
            # Position = progress of track if playback is paused. Else, it is the timestamp at which playback started (and leaves the client to render the seek bar)
            "position": self.get_track_progress() if not self.is_playing() else round(time.time() * 1000) - self.get_track_progress(),
            "current_track_length": self.get_track_length(),
            "is_playing": self.is_playing(),
            "volume": self.get_volume(),
            "is_muted": self.is_muted()
        }

    def playpause(self):
        raise NotImplementedError

    def is_playing(self) -> bool:
        raise NotImplementedError

    def is_finished(self) -> bool:
        raise NotImplementedError

    def play_next(self, track: Optional[Track]):
        raise NotImplementedError

    def get_current_track(self) -> Optional[Track]:
        raise NotImplementedError

    def get_track_length(self) -> int:
        raise NotImplementedError

    def get_track_progress(self) -> int:
        raise NotImplementedError

    def get_volume(self) -> int:
        raise NotImplementedError

    def vol_increase(self):
        raise NotImplementedError

    def vol_decrease(self):
        raise NotImplementedError

    def vol_mute_toggle(self):
        raise NotImplementedError

    def is_muted(self) -> bool:
        raise NotImplementedError
