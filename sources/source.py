from typing import Optional, Dict

from flask_socketio import SocketIO

from enums.download_status import DownloadStatus
from track import Track

import csv

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
        Attempts to download the file coresponding to the provided track
        """
        raise NotImplementedError
