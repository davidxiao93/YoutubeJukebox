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

    // user is seeking, TODO move to vue
//    $('#progress').on('input', function(event){
//        $('#time').html(convertToTime(event.target.value));
//        seek(event.target.value);
//    });
    
});






//emitted events

function toggleMedia(action) {
    //when play button is pressed play the audio element
    if (action == 'play') {
        document.getElementById('audio').play();
    }

    //when pause button is pressed pause the audio element
    else if (action == 'pause') {
        document.getElementById('audio').pause();
    }

    //when stop button is pressed stop the audio element
    else if (action == 'stop') {
        document.getElementById('audio').pause();
        document.getElementById('audio').currentTime = 0;
    }
};

function seek(value) {
    //conver ml to sec
    value = ((value % 60000) / 1000).toFixed(0);
    value = parseInt(value);
    
    //set the progress time of the audio element
    document.getElementById('audio').currentTime = value;
};

function changeVolume(value) {
    //convert percentage to decimal
    value = value / 100;
    
    //set the volume time of the audio element
    document.getElementById('audio').volume = value;
};

//emitted events end


function playTrack(track){
    //invoke the built-in function to set info of the track on the player
    setMediaInfo(track.cover, track.name, track.artists, 30000);
    
    //set the background of the page as the cover image
    $('#background').css('background-image', 'url(' + track.cover + ')');
    
    //set the audio source
    $('#audio').attr("src", track.preview);
    
    //set event listeners on the audio element
    $('#audio').on('playing', function(){toggleIcon('pause')});//on playing change fav icon
    $('#audio').on('pause', function(){toggleIcon('play')});//on playing change fav icon
    //set the progress bar of the player as media plays
    $('#audio').on('timeupdate', function(){
        var value = document.getElementById('audio').currentTime;
        value = ((value % 60000) * 1000).toFixed(0);
        updateProgress(value); //invoke the built-in function to update the progress bar
    });
};

function displayResults(data, max, toId) {
    $('#'+toId).html(""); //empty the display grid
    
    //inser results until max amount is reached
    var current = 0;
    for (var i in data) {
        if (current >= max) break;
        
        insertResult(data[i], toId);
        current++
    }
};

function insertResult(obj, toId) {
    //build the card object containing the cover, track title, and artists
    var item = "<div id='" + obj.id + "' class='card-image mdl-card mdl-shadow--2dp grid-item button' style='background-image: url(" + obj.cover + ")'><div class='mdl-card__title mdl-card--expand'></div><div class='mdl-card__supporting-text'><span>"+ obj.name +"</span><br>" + obj.artists + "</div></div>";
    
    //insert the card
    $('#'+toId).append(item);
    
    //set an event ilstener for when the user clicks the card
    $('#'+obj.id).click(function() {
        playTrack(obj);//play the track
    });
};