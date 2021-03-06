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


from flask import Flask, render_template
from flask_socketio import SocketIO

from enums.download_status import DownloadStatus
from players.VLCPlayer import VLCPlayer
from sources.YoutubeSource import YoutubeSource
from track_queue import TrackQueue


async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')


@app.route('/')
def index():
    return render_template('index.html')


player = VLCPlayer(socketio)
source = YoutubeSource(socketio)
track_queue = TrackQueue(socketio)


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
                    track_queue.push_queue_state()
                    print(e)
                    break

                socketio.sleep(1)

                # Try to download the actual file now
                try:
                    source.fetch_file(track.source_id)
                    track.download_status = DownloadStatus.CAPTURED
                    track_queue.push_queue_state()
                except Exception as e:
                    track.download_status = DownloadStatus.ERROR
                    track_queue.push_queue_state()
                    print(e)
                break

                # TODO: seeing as ffmpeg processing within youtube dl doesnt seem to behave, maybe make a separate state for ffmpeg processing

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
    action = message["action"]
    param = message["param"] if "param" in message else None
    if action == "getstate":
        player.push_now_playing_state()
        track_queue.push_queue_state()
    elif action == "volup":
        player.vol_increase()
    elif action == "voldown":
        player.vol_decrease()
    elif action == "voltoggle":
        player.vol_mute_toggle()
    elif action == "playnext":
        player.play_next(track_queue.get_next_track())
    elif action == "stop":
        player.stop_playing()
    elif action == "queueclear":
        track_queue.clear_queue()
    elif action == "queueadd":
        track_queue.add_track(source.build_track(param))
    elif action == "queueraise":
        track_queue.raise_track(int(param))
    elif action == "queuelower":
        track_queue.lower_track(int(param))
    elif action == "queueremove":
        track_queue.remove_track(int(param))
    else:
        print(f"Unknown action: {action}")


@socketio.event
def connect():
    player.push_now_playing_state()
    track_queue.push_queue_state()


if __name__ == '__main__':
    socketio.run(app)
