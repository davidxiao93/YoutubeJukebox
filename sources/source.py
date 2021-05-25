import os
from pathlib import Path
from typing import Optional, Dict

from eventlet import tpool
from expiringdict import ExpiringDict
from flask_socketio import SocketIO

from track.track import Track

import ffmpeg

from track.track_info import TrackInfo


class Source:

    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.search_cache: Dict[str, TrackInfo] = ExpiringDict(max_len=1_000, max_age_seconds=24*60*60)

    def build_track(self, query: str) -> Track:
        return Track(query)

    def check_cache(self, query: str) -> Optional[TrackInfo]:
        if query not in self.search_cache:
            return None
        return self.search_cache[query]

    def add_to_cache(self, query: str, track: Track):
        self.search_cache[query] = track.info

    def fetch_meta(self, query: str) -> Track:
        """
        Fills in the Track based on the source_id
        """
        raise NotImplementedError


    def fetch_file(self, source_id: str):
        """
        Attempts to download the file coresponding to the provided track.
        It should be stored under download/temp [no file extension]
        """
        raise NotImplementedError

    def process_file(self, track: Track):
        """
        Attempts to transcode the file in download/temp into the audio file
        """

        temp_file = Path("download/temp")
        if not temp_file.is_file():
            raise Exception("temp file doesn't exist")

        input_ffmpeg = ffmpeg.input("download/temp")
        input_audio = input_ffmpeg['a'] # We will not be referencing the video stream, only the main audio stream

        # Normalise loudness
        input_audio = ffmpeg.filter(input_audio, "loudnorm", I=-16, TP=-1.5, LRA=11)


        # https://superuser.com/questions/1362176/how-to-trim-silence-only-from-beginning-and-end-of-mp3-files-using-ffmpeg/1364824
        # Trim silence from start
        input_audio = ffmpeg.filter(input_audio, "silenceremove", start_periods=1, start_duration=1, start_threshold="-60dB", detection="peak")

        # No idea what this does
        input_audio = ffmpeg.filter(input_audio, "aformat", "dblp")

        # Reverse the audio
        input_audio = ffmpeg.filter(input_audio, "areverse")

        # Trim silence from start (but this track is reversed now, so this is trimming from the end
        input_audio = ffmpeg.filter(input_audio, "silenceremove", start_periods=1, start_duration=1, start_threshold="-60dB", detection="peak")

        # No idea what this does
        input_audio = ffmpeg.filter(input_audio, "aformat", "dblp")

        # Reverse the audio
        input_audio = ffmpeg.filter(input_audio, "areverse")

        output_ffmpeg = ffmpeg.output(input_audio, filename=f"download/{track.info.source_id}.mp3")
        output_ffmpeg = ffmpeg.overwrite_output(output_ffmpeg) # overwrite if needed


        def run_ffmpeg(output):
            return ffmpeg.run(output, quiet=True)

        # Force monkey patching to run this in the background in this supposed background task...
        tpool.execute(run_ffmpeg, output_ffmpeg)

        try:
            os.remove("download/temp")
        except:
            raise Exception("failed to delete temp file")
