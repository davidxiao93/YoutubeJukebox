import os
from pathlib import Path
from typing import Optional, Dict

from eventlet import tpool
from flask_socketio import SocketIO

from enums.download_status import DownloadStatus
from track import Track

import csv

import ffmpeg

TRACK_FIELDS = ["source_id", "title", "artist", "thumbnail", "duration"]
CSV_FIELDS = ["query"] + TRACK_FIELDS

class Source:

    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.search_cache: Optional[Dict[str, Dict[str, str]]] = None

    def build_track(self, query: str) -> Track:
        return Track(
            source_id=query,
            title="",
            artist="",
            thumbnail="",
            duration=0,
            download_status=DownloadStatus.QUEUED
        )

    def check_cache(self, query: str) -> Optional[Track]:
        if self.search_cache is None:
            self.search_cache = {}
            try:
                with open('search_cache.csv') as search_cache_file:
                    reader = csv.DictReader(search_cache_file, fieldnames=CSV_FIELDS)
                    for row in reader:
                        self.search_cache[row["query"]] = {}
                        for field in TRACK_FIELDS:
                            self.search_cache[row["query"]][field] = row[field]
            except FileNotFoundError as e:
                # Expected error if starting server from scratch, will be self handed when the file is created
                pass
            except:
                raise Exception("Failed to load file")

        if query not in self.search_cache:
            return None

        track_dict = self.search_cache[query]
        return Track(
            source_id=track_dict["source_id"],
            title=track_dict["title"],
            artist=track_dict["artist"],
            thumbnail=track_dict["thumbnail"],
            duration=int(track_dict["duration"]),
            download_status=DownloadStatus.QUEUED
        )

    def add_to_cache(self, query: str, track: Track):
        cache_dict = {
            "query": query,
            "source_id": track.source_id,
            "title": track.title,
            "artist": track.artist,
            "thumbnail": track.thumbnail,
            "duration": track.duration
        }
        try:
            with open('search_cache.csv', 'a') as search_cache_file:
                writer = csv.DictWriter(search_cache_file, fieldnames=CSV_FIELDS)
                writer.writerow(cache_dict)
        except:
            # If there is an error, oh well, we'll search again next time. No problem
            pass
        self.search_cache[query] = cache_dict
        return


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

        output_ffmpeg = ffmpeg.output(input_audio, filename=f"download/{track.source_id}.mp3")
        output_ffmpeg = ffmpeg.overwrite_output(output_ffmpeg) # overwrite if needed
        print(ffmpeg.compile(output_ffmpeg))


        def run_ffmpeg(output):
            return ffmpeg.run(output, quiet=True)

        # Force monkey patching to run this in the background in this supposed background task...
        tpool.execute(run_ffmpeg, output_ffmpeg)

        try:
            os.remove("download/temp")
        except:
            raise Exception("failed to delete temp file")
