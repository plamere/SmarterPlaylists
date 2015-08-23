var inventory = null
var editor = null;
var apiLocalPath = 'http://localhost:5000/SmarterPlaylists/';
var apiRemotePath = 'http://labs2.echonest.com/SmarterPlaylists/';

var client_id = 'bb61fcfe1423449ba3d8e3b016316316';
var local_redirect_uri = 'http://localhost:8000/callback.html';
var remote_redirect_uri = 'http://static.echonest.com/SmarterPlaylists/callback.html';
var local_auth_redirect_uri = 'http://localhost:8000/auth.html';
var remote_auth_redirect_uri = 'http://static.echonest.com/SmarterPlaylists/auth.html';

var apiPath = isLocalHost() ? apiLocalPath : apiRemotePath;
var redirect_uri = isLocalHost() ? local_redirect_uri : remote_redirect_uri;
var auth_redirect_uri = isLocalHost() ? local_auth_redirect_uri : remote_auth_redirect_uri;

var forceRemote = false;
var confirmDelete = true;


function get_auth_code() {
    return localStorage.getItem('sp-auth-code');
}

function clear_auth_code() {
    return localStorage.removeItem('sp-auth-code');
}

function isLocalHost() {
    if (forceRemote) {
        return false;
    } else {
        return window.location.host.indexOf('localhost') >= 0;
    }
}

var deltaNames = {
    0: "Never",
    60: "Once a minute",
    3600: "Once an hour",
    86400: "Once a day",
    604800: "Once a week",
    2592000: "Once a month",
}

function getDeltaName(delta) {
    delta = parseInt(delta);
    if (delta in deltaNames) {
        return deltaNames[delta];
    } else {
        return fmtTime(delta);
    }
}

function isValidDelta(val) {
    return val in deltaNames;
}

function info(s) {
    $("#info").text(s);
}

function fmtTime(secs) {
    function pad(v) {
        var vs = v.toString();
        if (vs.length == 1) {
            vs = '0' + vs;
        }
        return vs;
    }

    if (isNaN(secs)) {
        return "00:00:00";
    }

    var s = Math.round(secs);
    var d = Math.floor(s / (3600 * 24));
    s -= d * 3600 * 24;
    var h = Math.floor(s / 3600);
    s -= h * 3600;
    var m = Math.floor(s/60);
    s -= m * 60

    prefix = d > 0 ? d + "d " : "";
    if (h == 0) {
        return prefix + pad(m) + ":" + pad(s);
    } else {
        return prefix + pad(h) + ":" + pad(m) + ":" + pad(s);
    }
}


function checkForBadUser(data) {
    console.log(data.status, data.msg);
    if (data.status == 'error' && data.msg == 'no authorized user') {
        clear_auth_code();
        document.location = 'index.html';
    }
}

function fetchInventory(callback) {
    $.getJSON(apiPath + 'inventory').then(
        function(data) {
            checkForBadUser(data);
            var inventoryMap = {};
            _.each(data.inventory.components, function(component) {
                inventoryMap[component.name] = component;
            });
            callback(inventoryMap, data.inventory.types);
        },
        function() {
            callback(null);
        }
    );
}


function fetchScheduleStats(pid, callback) {
    $.getJSON(apiPath + 'schedule_status', {
        pid:pid,
        auth_code: get_auth_code()
    }).then(
        function(data) {
            checkForBadUser(data);
            callback(data);
        },
        function() {
            callback(null);
        }
    );
}

function fmtDate(ts) {
    if (ts) {
        var d = new Date(0);
        d.setUTCSeconds(ts);
        var out = d.toString().substring(0,21);
        return out;
    } else {
        return '';
    }
}

function showBuilder() {
    $('#tabs a[href="#work"]').tab('show'); // Select tab by name
}

function showDirectoryTable(dir) {
    var body = $("#dir-body");
    body.empty();
    /*
    dir.sort(function(a, b) {
        return b.last_run - a.last_run;
    });
    */

    _.each(dir, function(entry, i) {
        var tr = $("<tr>");

        tr.append( $("<td>").text( (i + 1) ));
        if (entry.uri) {
            tr.append( 
                $("<td>").append( 
                    $("<a>")
                        .attr('href', entry.uri)
                        .text(entry.name)
                        .on('click', function(e) {
                            e.stopPropagation();
                        })));
        } else {
            tr.append( $("<td>").text( entry.name ));
        }
        tr.append( $("<td>").text( fmtDate(entry.last_run) ));
        tr.append( $("<td>").text( entry.runs ));

        if (entry.shared) {
            var anchor = $("<a>")
                .text('shareable link')
                .attr('href', 'importer.html?pid=' + entry.pid);
            tr.append( $("<td>").append(anchor));
        } else {
            tr.append( $("<td>").text(''));
        }

        // show schedule status
        {
            var status = '';
            if (entry.schedule_status.status) {
                var ss = entry.schedule_status.status;
                if (ss  == 'queued' || ss == 'running') {
                    status = getDeltaName(entry.schedule_status.delta);
                } else {
                    status = entry.schedule_status.status
                }
            }
            tr.append( $("<td>").text(status));
        }
        if (true) {
            var controls = $("<td>");

            if (true) {
                var btn = getIconButton('glyphicon-edit');
                btn.attr('title', 'edit this program');
                btn.on('click', function(e) {
                    e.stopPropagation();
                    showBuilder();
                    loadProgram(inventory, entry.pid, function(program) {
                        editor.load(program);
                    });
                });
                controls.append(btn);
            }

            if (false) {
                var btn = getIconButton('glyphicon-edit');
                btn.attr('title', 'edit this program');
                btn.attr('href', 'edit.html?pid=' + entry.pid);
                controls.append(btn);
            }

            (function() {
                var btn = getIconButton('glyphicon-play-circle');
                btn.attr('title', 'run this program');
                btn.on('click', function(e) {
                    e.stopPropagation();
                    btn.addClass('icon-red');
                    runProgram(entry.pid, true, function(data) {
                        btn.removeClass('icon-red');
                        if (data) {
                            console.log(data);
                            if (data.status == 'ok') {
                                showPlaylist(entry.name, data);
                            } else {
                                error(data.message);
                            }
                        }
                        showDirectory();
                    });
                })
                controls.append(btn);
            })();


            {
                var btn = getIconButton('glyphicon-share');
                btn.attr('title', 'share this program');
                if (entry.shared) {
                    btn.addClass('icon-blue');
                } 

                btn.on('click', function(e) {
                    e.stopPropagation();
                    shareProgram(entry.pid, !entry.shared, function(results) {
                        showDirectory();
                    });
                })
                controls.append(btn);
            }

            {
                var btn = getIconButton('glyphicon-duplicate');
                btn.attr('title', 'copy this program');
                btn.on('click', function(e) {
                    e.stopPropagation();
                    copyProgram(entry.pid, function(results) {
                        console.log(results);
                        showDirectory();
                    });
                })
                controls.append(btn);
            }

            {
                var btn = getIconButton('glyphicon-time');
                btn.attr('href', 'schedule.html?pid=' + entry.pid);
                btn.attr('title', 'schedule this program to run periodically');
                controls.append(btn);

                if (entry.schedule_status.status) {
                    if (ss  == 'queued' || ss == 'running') {
                        btn.addClass('icon-blue');
                    }
                } 
            }

            {
                var btn = getIconButton('glyphicon-trash');
                btn.addClass('icon-red');
                btn.attr('title', 'delete this program');
                btn.on('click', function(e) {
                    e.stopPropagation();
                    if (confirmDelete) {
                        if (window.confirm('Delete ' + entry.name + '?')) {
                            removeProgram(entry.pid, function(status) {
                                showDirectory();
                            });
                        }
                    } else {
                        removeProgram(entry.pid, function(status) {
                            showDirectory();
                        });
                    }
                })
                controls.append(btn);
            }


            tr.append( controls);
        }
        body.append(tr);
    });
}

function getIconButton(icn) {
    var a = $("<a>")
        .addClass("icon-btn btn-lg active");
    var span = $("<span>")
        .addClass("glyphicon")
        .addClass(icn);
    a.append(span);
    return a;
}

function showDirectory() {
    loadProgramDirectory(function(results) {
        if (results.status == 'ok') {
            showDirectoryTable(results.programs);
        }
    });
}



function initApp() {    
    var params = parseParams();
    var pprogram = ('program' in params) ? params['program'] : null;

    
    $('a[data-toggle="tab"]').on('shown.bs.tab', function(e) {
        if ($(e.target).attr('href') == '#dir') {
            showDirectory();
        } else if ($(e.target).attr('href') == '#ttracks') {
            playlistShown();
        }
    });

    $("#save").on("click", function() {
        savePlaylist(function(ok) {
            if (ok) {
                info("Saved!");
            } else {
                error("not saved!");
            }
        });
    });

    $("#logout").on("click", function() {
        clear_auth_code();
        document.location = 'index.html';
    });


    var newButton = $("#new-button");
    newButton.on('click', function() {
        var name = 'untitled';
        var program = new Program(inventory, name);
        showBuilder();
        editor.load(program);
    });


    fetchInventory(function(inventoryMap, styles) {
        $("#spinner").hide();
        if (inventoryMap == null) {
            alert("Uh Oh - Having trouble phoning home");
        } else {
            $('#tabs').tab();
            inventory = inventoryMap;
            editor = createEditor("workspace", inventoryMap, styles);
            $('.nav-tabs a[href="#dir"]').tab('show');
        }
    });
}

function loginWithSpotifyForAuth() {
    var scopes = "playlist-read-private playlist-read-collaborative";

    scopes += " playlist-modify-public playlist-modify-private"
    scopes += " user-library-read"
    scopes += " user-follow-read"

    var url = 'https://accounts.spotify.com/authorize?client_id=' + client_id +
        '&response_type=code&show_dialog=false' +
        '&scope=' + scopes +
        '&redirect_uri=' + encodeURIComponent(auth_redirect_uri);

    document.location = url;
    //var w = window.open(url, 'asdf', 'WIDTH=400,HEIGHT=500');
}

function error(msg) {
    var alert= $("<div>")
        .addClass('alert')
        .addClass('alert-danger')
        .text(msg)
        .append( 
            $("<a>")
                .attr('href', '#')
                .addClass('close')
                .attr('data-dismiss', 'alert')
                .html("&times;"))
    $("#errors").append(alert);
}

function urldecode(str) {
   return decodeURIComponent((str+'').replace(/\+/g, '%20'));
}

function parseParams() {
    var params = {};
    var q = document.URL.split('?')[1];
    if(q != undefined){
        q = q.split('&');
        for(var i = 0; i < q.length; i++){
            var pv = q[i].split('=');
            var p = pv[0];
            var v = pv[1];
            params[p] = urldecode(v);
        }
    }
    return params;
}



