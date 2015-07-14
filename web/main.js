var inventory = null
var editor = null;
var apiPath = 'http://localhost:5000/sps/'


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
            console.log('inventory here', data);
            var inventoryMap = {};
            _.each(data.inventory.components, function(component) {
                inventoryMap[component.name] = component;
            });
            console.log('fi', data, inventoryMap);
            callback(inventoryMap, data.types);
        },
        function() {
            console.log('inventory trouble');
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
                            console.log('stop prp');
                        })));
        } else {
            tr.append( $("<td>").text( entry.name ));
        }
        tr.append( $("<td>").text( fmtDate(entry.extra.lastRun / 1000) ));
        tr.append( $("<td>").text( entry.extra.runs ));
        // tr.append( $("<td>").text( entry.extra.errors));
        tr.append( $("<td>").text( _.keys(entry.components).length));

        tr.on('click', function() {
            console.log('open', entry.name);
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
                            console.log('delete');
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


function initApp() {    
    $('a[data-toggle="tab"]').on('shown.bs.tab', function(e) {
        console.log('showing', e.target);
        if ($(e.target).attr('href') == '#dir') {
            showDirectory();
            console.log('showing dir');
        } else if ($(e.target).attr('href') == '#ttracks') {
            playlistShown();
            console.log('showing tracks');
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
    console.log('fetching inventory ...');
    fetchInventory(function(inventoryMap, styles) {
        if (inventoryMap == null) {
            alert("Uh Oh - Having trouble phoning home");
        } else {
            inventory = inventoryMap;
            editor = createEditor("workspace", inventoryMap, styles);
            var mostRecent = loadMostRecentProgram(inventory);
            if (mostRecent) {
                editor.load(mostRecent);
            } else {
                console.log('no recent program');
            }
        }
        console.log('inventory ready');
    });

}

function error(msg) {
    console.log('ERROR ' + msg);
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


$(document).ready(
    function() {
        initApp();
    }
);

