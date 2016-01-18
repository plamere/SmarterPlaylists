
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


function showPlaylist(name, data) {
    var tbody = $("#playlist-body");
    tbody.empty();


    $("#tab-track-count").text(data.tracks.length);
    $("#tab-track-count").addClass('tc-fresh');
    $("#playlist-title").text(name);
    $("#playlist-description").text(data.name);


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


function loginWithSpotify() {
    var url = 'https://accounts.spotify.com/authorize?client_id=' + client_id +
        '&response_type=token' +
        '&scope=playlist-modify-private' +
        '&redirect_uri=' + encodeURIComponent(redirect_uri);
    var w = window.open(url, 'asdf', 'WIDTH=400,HEIGHT=500');
}
