var inventory = null
var editor = null;
var apiLocalPath = 'http://localhost:5000/SmarterPlaylists/';
var apiRemotePath = 'http://labs2.echonest.com/SmarterPlaylists/';

var client_id = 'bb61fcfe1423449ba3d8e3b016316316';
var local_redirect_uri = 'http://localhost:8000/callback.html';
var remote_redirect_uri = 'http://static.echonest.com/SmarterPlaylists/callback.html';

var apiPath = isLocalHost() ? apiLocalPath : apiRemotePath;
var redirect_uri = isLocalHost() ? local_redirect_uri : remote_redirect_uri;

var forceRemote = false;


function isLocalHost() {
    if (forceRemote) {
        return false;
    } else {
        return window.location.host.indexOf('localhost') >= 0;
    }
}

function error(s) {
    console.log('ERROR ' + s);
    $("#info").text(s);
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
    var d = new Date(0);
    d.setUTCSeconds(ts);
    var out = d.toString().substring(0,21);
    return out;
}

function showBuilder() {
    $('#tabs a[href="#work"]').tab('show') // Select tab by name
}

function showInitialDirectory() {
    loadInitialDirectory(inventory, function() {
        showDirectory();
    });
}

function showDirectory() {
    var body = $("#dir-body");
    body.empty();
    var dir = loadDirectory(inventory);

    dir.sort(function(a, b) {
        return b.extra.lastRun - a.extra.lastRun;
    });

    _.each(dir, function(entry, i) {
        var tr = $("<tr>");

        tr.append( $("<td>").text( (i + 1) ));
        if (entry.extra.uri) {
            tr.append( 
                $("<td>").append( 
                    $("<a>")
                        .attr('href', entry.extra.uri)
                        .text(entry.name)
                        .on('click', function(e) {
                            e.stopPropagation();
                        })));
        } else {
            tr.append( $("<td>").text( entry.name ));
        }
        tr.append( $("<td>").text( fmtDate(entry.extra.lastRun / 1000) ));
        tr.append( $("<td>").text( entry.extra.runs ));
        // tr.append( $("<td>").text( entry.extra.errors));
        tr.append( $("<td>").text( _.keys(entry.components).length));

        tr.on('click', function() {
            showBuilder();
            editor.load(entry);
        });
        if (true) {
            var controls = $("<td>");
                /*
                controls.append(
                    $("<a>")
                        .addClass('prog-but')
                        .text('edit')
                        .on('click', function(e) {
                            console.log('edit');
                            e.stopPropagation();
                        })
                    );
                controls.append(
                    $("<a>")
                        .addClass('prog-but')
                        .text('run')
                        .on('click', function(e) {
                            console.log('run');
                            e.stopPropagation();
                        })
                    );
                */

                controls.append(
                    $("<a>")
                        .addClass('prog-but text-danger')
                        .text('Delete')
                        .on('click', function(e) {
                            e.stopPropagation();
                            if (window.confirm('Delete ' + entry.name + '?')) {
                                removeProgram(entry.name);
                                showDirectory();
                            }
                        })
                    );

            tr.append( controls);
        }
        body.append(tr);
    });
}

function loadRemoteProgram(path, inventory, callback) {
    $.getJSON(path).then(
        function(sprog) {
            delete sprog.extra.uri;
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
    
    $('a[data-toggle="tab"]').on('shown.bs.tab', function(e) {
        if ($(e.target).attr('href') == '#dir') {
            showInitialDirectory();
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



