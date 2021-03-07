$(function(){
    var socket = io();
    const app = new Vue({
        el: "#app",
        data: {
            now_playing: {},
            queue: []
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
            now_playing_duration: function() {
                if (this.now_playing?.current_track?.duration) {
                    return Math.round(this.now_playing.current_track.duration/60) + ":" + this.now_playing.current_track.duration%60;
                }
                return "--:--";
            }
        }
    })

    socket.on('now_playing', function(msg, cb) {
        app.now_playing = msg;
    });

    socket.on('queue', function(msg, cb) {
        app.queue = msg;
    });

    // New Search
    $('form').on('submit', function(event) {
        event.preventDefault(); //prevent page from reloading
        var val = $('#inputText').val(); //get the text from the input
        socket.emit('command', {action: 'queueadd', param: val});
        $('#inputText').val('');
    });

    // Mute
    $('#volumemute').on('click',function(){
        socket.emit('command', {action: 'voltoggle'});
    });
    // User changed volume
    $('#volume').on('input', function(event) {
        socket.emit('command', {action: 'volset', param: event.target.value});
    });
    // user is seeking
    $('#progress').on('input', function(event){
        $('#time').html(convertToTime(event.target.value));
        seek(event.target.value);
    });
    
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