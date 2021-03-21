function seconds_string(num_seconds) {
    const minutes = Math.floor(num_seconds/60);
    const seconds = num_seconds%60;
    return minutes + ":" + String(seconds).padStart(2, '0');
}

$(function(){
    var socket = io();
    const app = new Vue({
        el: "#app",
        data: {
            now_playing: {},
            queue: [],
            progress: 0,
            DOWNLOAD_STATUS: {
                QUEUED: 0,
                SEARCHING: 1,
                DOWNLOADING: 2,
                PROCESSING: 3,
                CAPTURED: 4,
                ERROR: 5
            }
        },
        computed: {
            now_playing_thumbnail: function() {
                if (this.now_playing?.current_track?.thumbnail_url) {
                    return this.now_playing.current_track.thumbnail_url;
                }
                return "static/images/artwork-not-found.png";
            },
            now_playing_title: function() {
                if (this.now_playing?.current_track?.title) {
                    return this.now_playing.current_track.title;
                }
                return "--";
            },
            now_playing_artist: function() {
                if (this.now_playing?.current_track?.artist) {
                    return this.now_playing.current_track.artist;
                }
                return "--";
            },
            now_playing_progress: function() {
                if (this.now_playing.is_playing) {
                    return seconds_string(this.progress);
                }
                return "--:--";
            },
            now_playing_duration: function() {
                if (this.now_playing?.current_track?.duration) {
                    return seconds_string(this.now_playing.current_track.duration);
                }
                return "--:--";
            },
            display_volume: function() {
                return String(this.now_playing.volume).padStart(3, '0');
            },
            progress_bar_max: function() {
                if (this.now_playing?.current_track?.duration) {
                    return this.now_playing.current_track.duration;
                }
                return 1;
            }
        },
        methods: {
            onSearch: function(event) {
                var query = event.target.elements.inputText.value;
                socket.emit('command', {action: 'queueadd', param: query});
                event.target.reset(); // Clear the form
            },
            onVolMute: function() {
                socket.emit('command', {action: 'voltoggle'});
            },
            onVolChange: function() {
                socket.emit('command', {action: 'volset', param: this.now_playing.volume});
            },
            onRemoveTrack: function(index) {
                socket.emit('command', {action: 'queueremove', param: index})
            },
            onSeek: function() {
                socket.emit('command', {action: 'playseek', param: this.progress})
            },
            onPlayNext: function() {
                socket.emit('command', {action: 'playnext'})
            }
        },
        updated() {
            // Get mdl magic upgrade thingy to work!
            this.$nextTick(() => {
                componentHandler.upgradeDom();
                componentHandler.upgradeAllRegistered();
            });
        },
        mounted: function() {
            window.setInterval(() => {
                this.progress = Math.min(this.progress_bar_max, parseInt(this.progress) + 1);
            }, 1000);
        }
    });

    socket.on('now_playing', function(msg, cb) {
        app.now_playing = msg;
        if (app.now_playing.is_playing) {
            const expected_progress = Math.round(Date.now() / 1000) - app.now_playing.started;
            if (app.progress !== expected_progress) {
                app.progress = expected_progress;
            }
        }
    });

    socket.on('queue', function(msg, cb) {
        app.queue = msg;
    });
    
});
