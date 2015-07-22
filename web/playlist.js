
var curTracks = [];
var curProgram = null;
var audio = null;

function play(url) {
    if (audio == null) {
        audio = $("<audio>");
    }

    if (!audioIsPaused()) {
        audio.get(0).pause();
        if (audio.attr('src') == url) {
            return;
        } 
    }
    audio.attr('src', url);
    audio.get(0).play();
}

function audioIsPaused() {
    return audio.get(0).paused;
}

function stopTrack() {
    if (audio) {
        audio.get(0).pause();
    }
}


function showPlaylist(program, data) {
    var name = program.name;
    var tbody = $("#playlist-body");
    tbody.empty();


    $("#tab-track-count").text(data.tracks.length);
    $("#tab-track-count").addClass('tc-fresh');
    $("#playlist-title").text(name);
    $("#playlist-description").text(data.name);

    curTracks = data.tracks;
    curProgram = program;

    if (program == null || data.tracks.length == 0) {
        $("#save").prop("disabled", true);
    } else {
        $("#save").prop("disabled", false);
    }

    _.each(data.tracks, function(track, i) {
        var tr = $("<tr>");
        var count = $("<td>").text(i + 1);
        var title = $("<td>").text(track.title);
        var artist = $("<td>").text(track.artist);
        var src = $("<td>").text(track.src);
        tr.append(count);
        tr.append(title);
        tr.append(artist);
        tr.append(src);
        tbody.append(tr);

        title.on('click', function() {
            if (track.spotify && track.spotify.preview_url) {
                play(track.spotify.preview_url);
            } else {
                fetchSpotifyTrackInfo(track.id, function(spotify_track_info) {
                    if (spotify_track_info) {
                        track.spotify = spotify_track_info;
                        play(track.spotify.preview_url);
                    }
                });
            }
            console.log('playing', track);
        });
        title.addClass('playable');
    });
}

function fetchSpotifyTrackInfo(tid, callback) {
    var url = 'https://api.spotify.com/v1/tracks/' + tid;
    $.getJSON(url).then(
        function(trackInfo) {
            callback(trackInfo);
        },
        function() {
            callback(null);
        }
    );
}

function playlistShown() {
    $("#tab-track-count").removeClass('tc-fresh');
}


function savePlaylist() {
    var tracks = curTracks;
    if (curProgram && tracks && tracks.length > 0) {
        var tids = [];
        _.each(tracks, function(track) {
            tids.push('spotify:track:' + track.id);
        });
        localStorage.setItem('playlist-tids', JSON.stringify(tids));
        localStorage.setItem('playlist-title', curProgram.name);
        if (curProgram.extra.uri) {
            localStorage.setItem('playlist-uri', curProgram.extra.uri);
        } else {
            localStorage.removeItem('playlist-uri');
        }
        loginWithSpotify();
    }
}

function loginWithSpotify() {
    var client_id = 'bb61fcfe1423449ba3d8e3b016316316';
    var redirect_uri = 'http://localhost:8000/callback.html';
    var url = 'https://accounts.spotify.com/authorize?client_id=' + client_id +
        '&response_type=token' +
        '&scope=playlist-modify-private' +
        '&redirect_uri=' + encodeURIComponent(redirect_uri);
    var w = window.open(url, 'asdf', 'WIDTH=400,HEIGHT=500');
}

