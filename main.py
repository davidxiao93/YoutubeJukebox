#!/usr/bin/env python

"""
TODO: install script
- Download repo
- Install python3
- Install pip3
- Install requirements.txt
- Install youtube-dl (https://askubuntu.com/a/792022)
- Install ffmpeg
- Install vlc-bin
- Weekly cronjob to update everything
- Weekly cronjob to clean cache (https://stackoverflow.com/questions/11618144/bash-script-to-limit-a-directory-size-by-deleting-files-accessed-last)
- start server on boot

"""
from typing import Optional

from flask import Flask
from flask_socketio import SocketIO

from enums.download_status import DownloadStatus
from favourites.favourites import Favourites
from players.VLCPlayer import VLCPlayer
from sources.YoutubeSource import YoutubeSource
from track.track import Track
from track.track_queue import TrackQueue


async_mode = None

app = Flask(__name__,
            static_folder='static')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')
socketio.init_app(app, cors_allowed_origins="*")


@app.route('/')
def index():
    return app.send_static_file('index.html')

favourites = Favourites(socketio)
player = VLCPlayer(socketio, favourites)
source = YoutubeSource(socketio)
track_queue = TrackQueue(socketio, favourites)


def background_download_thread():
    # decides what needs to be downloaded (if any) and then proceeds to download it
    while True:
        socketio.sleep(1)
        for index, track in enumerate(track_queue.queue):
            if track.download_status == DownloadStatus.QUEUED:
                track.download_status = DownloadStatus.SEARCHING
                track_queue.push_queue_state()

                # Search for the source id
                try:
                    track = source.fetch_meta(track)
                    track.download_status = DownloadStatus.DOWNLOADING
                    track_queue.push_queue_state()
                except Exception as e:
                    track.download_status = DownloadStatus.ERROR
                    track.error = f"Failed to search for {track.query}, reason: {e}"
                    track_queue.push_queue_state()
                    print(e)
                    break

                socketio.sleep(1)

                # Try to download the actual file now
                try:
                    cached = source.fetch_file(track.info.source_id)
                    track.download_status = DownloadStatus.CAPTURED if cached else DownloadStatus.PROCESSING
                    track_queue.push_queue_state()
                except Exception as e:
                    track.download_status = DownloadStatus.ERROR
                    track.error = f"Failed to download for {track.info.title}, reason: {e}"
                    track_queue.push_queue_state()
                    print(e)
                    break

                if track.download_status == DownloadStatus.PROCESSING:
                    # Now try to do some post processing
                    try:
                        source.process_file(track)
                        track.download_status = DownloadStatus.CAPTURED
                        track_queue.push_queue_state()
                    except Exception as e:
                        track.download_status = DownloadStatus.ERROR
                        track.error = f"Failed to download for {track.info.title}, reason: {e}"
                        track_queue.push_queue_state()
                        print(e)
                        break


def background_queuer_thread():
    # pushes new tracks into the player automatically
    while True:
        socketio.sleep(1)
        if len(track_queue.queue) > 0:
            track = track_queue.queue[0]
            if track.download_status == DownloadStatus.CAPTURED and player.is_finished():
                player.play_next(track_queue.get_next_track())
        elif player.is_finished():
            player.play_next(track_queue.get_next_track())

socketio.start_background_task(background_download_thread)
socketio.start_background_task(background_queuer_thread)

@socketio.event
def command(message):
    # Yes, I'm fully aware that this could have (and perhaps should have) been done as a REST endpoint(s)
    # but I wanted to play with websockets m'kay
    action = message["action"]
    param = message["param"] if "param" in message else None
    if action == "getstate":
        player.push_now_playing_state()
        track_queue.push_queue_state()
        favourites.push_favourites_state()
    elif action == "volset":
        # param is expected to be a value between 0 and 100 inclusive
        player.set_volume(int(param))
    elif action == "voltoggle":
        player.vol_mute_toggle()
    elif action == "playnext":
        player.play_next(track_queue.get_next_track())
    elif action == "playseek":
        # param is expected to be seek position in whole seconds
        player.seek_to(int(param))
    elif action == "stop":
        player.stop_playing()
    elif action == "queueclear":
        track_queue.clear_queue()
    elif action == "queueadd":
        # param is expected to be the desired search query
        track_queue.add_track(source.build_track(param))
    elif action == "queueraise":
        # param is expected to be the index of the track to move up
        track_queue.raise_track(int(param))
    elif action == "queuelower":
        # param is expected to be the index of the track to move down
        track_queue.lower_track(int(param))
    elif action == "queueremove":
        # param is expected to be the index of the track to remove
        track_queue.remove_track(int(param))
    elif action == "favouriteadd" or action == "favouriteremove":
        index = int(param)
        maybe_track: Optional[Track]
        if index < 0:
            maybe_track = player.current_track
        else:
            maybe_track = track_queue.get_track_at(index)
        if maybe_track:
            if action == "favouriteadd":
                favourites.add_favourite(maybe_track.info)
            else:
                favourites.remove_favourite(maybe_track.info)
            player.push_now_playing_state()
            track_queue.push_queue_state()
    elif action == "favouritedelete":
        favourites.delete_favourite(param)
        player.push_now_playing_state()
        track_queue.push_queue_state()
    else:
        print(f"Unknown action: {action}")


@socketio.event
def connect():
    player.push_now_playing_state()
    track_queue.push_queue_state()
    favourites.push_favourites_state()


if __name__ == '__main__':
    socketio.run(app)
