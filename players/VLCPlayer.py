from typing import Dict, Union, Optional
from players.player import Player
from track import Track

import vlc



class VLCPlayer(Player):

    def __init__(self):
        super().__init__()
        self.vlc_instance = vlc.Instance()
        self.vlc_player = self.vlc_instance.media_player_new()

        self.muted = False # Don't rely on vlc muted state
        self.last_volume = 50
        self.vlc_player.audio_set_volume(self.last_volume)

    def playpause(self):
        if self.is_playing():
            self.vlc_player.pause()
        else:
            self.vlc_player.play()

    def is_playing(self) -> bool:
        return self.vlc_player.is_playing()

    def is_finished(self) -> bool:
        current_state = self.vlc_player.get_state()
        print(f"current_state, {current_state}")
        # 6 = Ended, 5 = Stopped
        return current_state in [
            vlc.State(0), # Nothing special
            vlc.State(5), # Stopped
            vlc.State(6), # Ended
            vlc.State(7)  # Error
        ]

    def play_next(self, track: Optional[Track]):
        self.current_track = track
        if track is not None:
            print("play next")
            # do something to fetch the source
            self.vlc_player.set_media(self.vlc_instance.media_new("/home/david/PycharmProjects/YoutubeJukebox/test.mp3"))
            self.vlc_player.play()
            self.current_track = track

    def get_track_length(self) -> int:
        return self.vlc_player.get_length()

    def get_track_progress(self) -> int:
        return self.vlc_player.get_time()

    def get_volume(self) -> int:
        return self.vlc_player.audio_get_volume()

    def set_volume(self, new_volume: int):
        if 0 <= new_volume <= 100:
            self.vlc_player.audio_set_volume(new_volume)
            self.last_volume = new_volume

    def vol_increase(self):
        self.set_volume(self.get_volume() + 10)

    def vol_decrease(self):
        self.set_volume(self.get_volume() - 10)

    def vol_mute_toggle(self):
        if self.is_muted():
            self.set_volume(self.last_volume)
            self.muted = False
        else:
            self.set_volume(0)
            self.muted = True

    def is_muted(self) -> bool:
        return self.muted
