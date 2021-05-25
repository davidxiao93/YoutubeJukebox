from flask_socketio import SocketIO

from favourites.favourites import Favourites
from players.player import Player

import os
import signal
import time

from eventlet.green import subprocess

# Implementation inspired by https://github.com/hansegucker/mediaserver

class VLCPlayer(Player):

    def __init__(self, socketio: SocketIO, favourites: Favourites):
        super().__init__(socketio, favourites)

    def is_playing(self) -> bool:
        if self.process is None:
            return False
        return self.process.poll() is None

    def is_finished(self) -> bool:
        if self.process is None:
            return True
        return self.process.poll() is not None

    def seek_to(self, start: int):
        if self.current_track is None:
            self.stop_playing()
            self.clear_track()
        else:
            if self.is_playing():
                self.stop_playing()
            self.current_track_started = int(time.time()) - start
            self.process = subprocess.Popen([
                "cvlc",
                "-q",                       # Shut it up
                "--start-time", str(start), # Start at a specific time
                "--play-and-exit",          # Close process when finished
                # TODO: do something to make sure that vlc volume is always 100%
                "download/" + self.current_track.info.source_id + ".mp3"
            ])
        self.push_now_playing_state()

    def stop_playing(self):
        if self.process is not None:
            try:
                os.kill(self.process.pid, signal.SIGTERM)
            except ProcessLookupError as e:
                # Do nothing
                pass
            except Exception as e:
                print(e)
            self.process = None

