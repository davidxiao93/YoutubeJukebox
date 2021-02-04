from typing import Optional

import vlc
from flask_socketio import SocketIO

from players.player import Player
from track import Track


class VLCPlayer(Player):

    def __init__(self, socketio: SocketIO):
        super().__init__(socketio)
        self.vlc_instance = vlc.Instance()
        self.vlc_player = self.vlc_instance.media_player_new()
        self.vlc_event_manager = self.vlc_player.event_manager()

        self.muted = False # Don't rely on vlc muted state
        self.last_volume = 50
        self.vlc_player.audio_set_volume(self.last_volume)


        def update_now_playing_state(event):
            self.push_now_playing_state()

        def play_next_track(event):
            self.socketio.emit("command", {"action": "playnext"})

        self.vlc_event_manager.event_attach(vlc.EventType.MediaPlayerPlaying, update_now_playing_state)
        self.vlc_event_manager.event_attach(vlc.EventType.MediaPlayerPaused, update_now_playing_state)
        self.vlc_event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, play_next_track)
        self.vlc_event_manager.event_attach(vlc.EventType.MediaPlayerMuted, update_now_playing_state)
        self.vlc_event_manager.event_attach(vlc.EventType.MediaPlayerUnmuted, update_now_playing_state)
        self.vlc_event_manager.event_attach(vlc.EventType.MediaPlayerAudioVolume, update_now_playing_state)

    def playpause(self):
        if self.is_playing():
            self.vlc_player.pause()
        else:
            self.vlc_player.play()

    def is_playing(self) -> bool:
        return self.vlc_player.is_playing()

    def is_finished(self) -> bool:
        current_state = self.vlc_player.get_state()
        return current_state in [
            vlc.State(0), # Nothing special
            vlc.State(5), # Stopped
            vlc.State(6), # Ended
            vlc.State(7)  # Error
        ]

    def play_next(self, track: Optional[Track]):
        self.current_track = track
        if track is not None:
            # do something to fetch the source
            self.vlc_player.set_media(self.vlc_instance.media_new("/home/david/PycharmProjects/YoutubeJukebox/test.mp3"))
            self.vlc_player.play()

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
            old_volume = self.get_volume()
            self.set_volume(0)
            self.last_volume = old_volume
            self.muted = True

    def is_muted(self) -> bool:
        return self.muted
