from flask_socketio import SocketIO

from players.player import Player

import os
import signal
import time

from eventlet.green import subprocess

# Implementation inspired by https://github.com/hansegucker/mediaserver

class VLCPlayer(Player):

    def __init__(self, socketio: SocketIO):
        super().__init__(socketio)

    def is_playing(self) -> bool:
        if self.process is None:
            return False
        return self.process.poll() is None

    def is_finished(self) -> bool:
        if self.process is None:
            return True
        return self.process.poll() is not None

    def start_playing(self):
        if self.current_track is not None:
            self.current_track_started = int(time.time())
            self.process = subprocess.Popen([
                "cvlc", "-f", "--no-osd", "--play-and-exit",
                "download/" + self.current_track.source_id + ".mp3"
            ])
        else:
            self.stop_playing()
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
        if self.current_track is not None:
            self.current_track = None
            self.push_now_playing_state()

