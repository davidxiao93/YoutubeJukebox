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
# Use None to let application decide which mode to use
socketio = SocketIO(app, async_mode=None)


@app.route('/')
def index():
    return render_template('index.html')


player = VLCPlayer()
source = YoutubeSource()
track_queue = TrackQueue()


def push_now_playing_state():
    socketio.emit("now_playing", player.build_state())

def push_queue_state():
    socketio.emit("queue", track_queue.build_state())


def background_download_thread():
    # decides what needs to be downloaded (if any) and then proceeds to download it
    while True:
        socketio.sleep(1)
        for index, track in enumerate(track_queue.queue):
            if track.download_status == DownloadStatus.QUEUED:
                track.download_status = DownloadStatus.DOWNLOADING
                push_queue_state()
                new_status = DownloadStatus.CAPTURED if source.fetch_file(track.source_id) else DownloadStatus.ERROR
                track.download_status = new_status
                push_queue_state()
                break

socketio.start_background_task(background_download_thread)


def background_queue_pusher_thread():
    # moves items from the queue into the player automatically
    # I would have made vlc player emit an "playnext" event, but the vlc integration has no callback for when something finishes
    while True:
        socketio.sleep(1)
        if not player.is_finished():
            continue
        player.play_next(track_queue.get_next_track())
        push_now_playing_state()
        push_queue_state()

socketio.start_background_task(background_queue_pusher_thread)


@socketio.event
def command(message):
    action = message["action"]
    param = message["param"] if "param" in message else None
    if action == "getstate":
        push_now_playing_state()
        push_queue_state()
    elif action == "volup":
        player.vol_increase()
        push_now_playing_state()
    elif action == "voldown":
        player.vol_decrease()
        push_now_playing_state()
    elif action == "voltoggle":
        player.vol_mute_toggle()
        push_now_playing_state()
    elif action == "playtoggle":
        player.playpause()
        push_now_playing_state()
    elif action == "playnext":
        player.play_next(track_queue.get_next_track())
        push_now_playing_state()
        push_queue_state()
    elif action == "queueclear":
        track_queue.clear_queue()
        push_queue_state()
    elif action == "queueadd":
        new_track = source.fetch_meta(param)
        track_queue.add_track(new_track)
        push_queue_state()
    elif action == "queueraise":
        track_queue.raise_track(int(param))
        push_queue_state()
    elif action == "queuelower":
        track_queue.lower_track(int(param))
        push_queue_state()
    elif action == "queueremove":
        track_queue.remove_track(int(param))
        push_queue_state()
    else:
        print(f"Unknown action: {action}")


@socketio.event
def connect():
    push_queue_state()
    push_now_playing_state()


@socketio.on('disconnect')
def test_disconnect():
    pass


if __name__ == '__main__':
    socketio.run(app)


"""
playtoggle causes wrong position to be sent?

playnext when queue is empty should do what?

voltoggle doesnt work
"""