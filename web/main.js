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
var confirmDelete = false;


function get_auth_code() {
    return localStorage.getItem('sp-auth-code');
}

function isLocalHost() {
    if (forceRemote) {
        return false;
    } else {
        return window.location.host.indexOf('localhost') >= 0;
    }
}

function info(s) {
    $("#info").text(s);
}

function fetchInventory(callback) {
    $.getJSON(apiPath + 'inventory').then(
        function(data) {
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
    $('#tabs a[href="#work"]').tab('show') // Select tab by name
}

function showDirectoryTable(dir) {
    var body = $("#dir-body");
    body.empty();
    dir.sort(function(a, b) {
        return b.last_run - a.last_run;
    });

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
        tr.append( $("<td>").text( entry.ncomponents));

        /*
        tr.on('click', function() {
            showBuilder();
            loadProgram(inventory, entry.pid, function(program) {
                editor.load(program);
            });
        });
        */
        if (true) {
            var controls = $("<td>");

                controls.append(
                    $("<a>")
                        .addClass('prog-but text-primary')
                        .text('Edit')
                        .on('click', function(e) {
                            e.stopPropagation();
                            showBuilder();
                            loadProgram(inventory, entry.pid, function(program) {
                                editor.load(program);
                            });
                        })
                    );

                controls.append(
                    $("<a>")
                        .addClass('prog-but text-primary')
                        .text('Run')
                        .on('click', function(e) {
                            e.stopPropagation();
                            runProgram(entry.pid, true, function(data) {
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
                    );

                controls.append(
                    $("<a>")
                        .addClass('prog-but text-primary')
                        .text('Copy')
                        .on('click', function(e) {
                            e.stopPropagation();
                        })
                    );

                controls.append(
                    $("<a>")
                        .addClass('prog-but text-primary')
                        .text('Share')
                        .on('click', function(e) {
                            e.stopPropagation();
                        })
                    );

                controls.append(
                    $("<a>")
                        .addClass('prog-but text-primary')
                        .text('Schedule')
                        .on('click', function(e) {
                            scheduleProgram(entry.pid, function(data) {
                                if (data) {
                                    console.log(data);
                                    if (data.status == 'ok') {
                                        info('job scheduled');
                                    } else {
                                        error(data.message);
                                    }
                                }
                                showDirectory();
                            });
                        })
                    );

                controls.append(
                    $("<a>")
                        .addClass('prog-but text-danger')
                        .text('Delete')
                        .on('click', function(e) {
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
                    );


            tr.append( controls);
        }
        body.append(tr);
    });
}

function showDirectory() {
    loadProgramDirectory(function(results) {
        if (results.status == 'ok') {
            showDirectoryTable(results.programs);
        }
    });
}

function loadRemoteProgram(path, inventory, callback) {
    $.getJSON(path).then(
        function(sprog) {
            var program = loadProgramFromJSON(inventory, sprog);
            callback(program);
        },
        function() {
            callback(null);
        }
    );
}


function initApp() {    
    var params = parseParams();
    var pprogram = ('program' in params) ? params['program'] : null;

    if ('pid' in params) {
        var pid = params['pid'];
        pprogram = apiPath + 'shared?pid='  + pid;
        console.log('pprogram', pprogram);
    }
    
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


    var newButton = $("#new-button");
    newButton.on('click', function() {
        var name = 'untitled';
        var program = new Program(inventory, name);
        showBuilder();
        editor.load(program);
    });


    $('#tabs').tab();
    fetchInventory(function(inventoryMap, styles) {
        if (inventoryMap == null) {
            alert("Uh Oh - Having trouble phoning home");
        } else {
            inventory = inventoryMap;
            editor = createEditor("workspace", inventoryMap, styles);
            if (pprogram) {
                loadRemoteProgram(pprogram, inventory, function(remoteProgram) {
                    if (remoteProgram) {
                        editor.load(remoteProgram);
                    } else {
                        error("Can't load " + pprogram);
                    }
                });
            } else {
                var mostRecent = loadMostRecentProgram(inventory);
                if (mostRecent) {
                    editor.load(mostRecent);
                } else {
                    $('.nav-tabs a[href="#dir"]').tab('show');
                }
            }
        }
    });
}

function loginWithSpotifyForAuth() {
    var scopes = "playlist-read-private playlist-read-collaborative";

    scopes += " playlist-modify-public playlist-modify-private"
    scopes += " user-library-read"

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



