#!/usr/bin/env python

"""
TODO:
update script that runs daily to update youtube-dl

Dependencies
- youtube-dl to download youtube videos (https://askubuntu.com/a/792022)
    get mp3 whilst downloading least? https://stackoverflow.com/a/64526840
    youtube-dl -f "bestaudio/best" -ciw -o "%(title)s.%(ext)s" -v --extract-audio --audio-quality 0 --audio-format mp3  https://www.youtube.com/watch?v=c29tZVZpZGVvUGxheWxpc3RQYXJ0
- ffmpeg to convert to mp3
- vlc? to play back mp3



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
socketio = SocketIO(app, async_mode='threading')


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
            if index == 0 and track.download_status == DownloadStatus.CAPTURED and player.is_finished():
                player.play_next(track_queue.get_next_track())
                break

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

socketio.start_background_task(background_download_thread)

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
    elif action == "playtoggle":
        player.playpause()
    elif action == "playnext":
        player.play_next(track_queue.get_next_track())
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


@socketio.on('disconnect')
def test_disconnect():
    pass


if __name__ == '__main__':
    socketio.run(app)
