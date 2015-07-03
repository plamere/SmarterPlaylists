
var createProgram = function(inventory, name) {

    var program = {
        name: name,
        components: {}
    }

    function createComponent(name, type, params, extra) {
        var component = {
            name: name,
            type: type,
            cls: inventory[type],
            params: params,
            extra: extra,
            outputs: []
        }

        if (component.cls.type == 'source') {
            component.maxInputs = 0;
        } else if (component.cls.type == 'multi-in-filter') {
            component.maxInputs = 20;
            component.source_list = [];
        } else {
            component.maxInputs = 1;
            component.source =  null;
        }
        return component;
    }

    function hasMultiSource(component) {
        return component.maxInputs > 1;
    }

    function extract(c) {
        var out = { 
            _type: c.type
        }

        if (c.source) {
            out.source = c.source;
        }

        if (c.source_list) {
            out.source_list = c.source_list.slice();
        }
        _.extendOwn(out, c.params);
        return out;
    }

    return {    
        addComponent: function(name, type, params, extra) {
            if (type == 'SpotifyPlaylist') {
                params.name = "Your Favorite Coffeehouse";
            }
            // 
            var c = createComponent(name, type, params, extra)
            if (name in program) {
                console.log('dup cname', name);
            }
            program.components[name] = c;
            return c;
        },

        removeComponent: function(name) {
            if (name in program.components) {
                delete program.components[name];
            }
        },

        addConnection: function(name1, name2) {
            console.log('ac', name1, name2, program);
            var c2 = program.components[name2];
            if (hasMultiSource(c2)) {
                c2.source_list.push(name1);
            } else {
                c2.source = name1;
            }
        },

        removeConnection: function(name1, name2) {
            var c2 = program.components[name2];
            if (hasMultiSource(c2)) {
                var idx = c2.source_list.indexOf(name1);
                if (idx >= 0) {
                    c2.source_list.splice(idx, 1);
                }
            } else {
                if (c2.source == name1) {
                    c2.source = null;
                }
            }
        },

        getComponent: function(name) {
            return program.components[name];
        },

        getComponents: function() {
            return program.components;
        },

        toJson: function(rootComponentName) {
            var jsonProgram = {
                main : rootComponentName,
                components : {},
            }
            _.each(program.components, function(component) {
                var name = component.name;
                jsonProgram.components[name] = extract(component);
            });

            return jsonProgram;
        }
    }
}

function postProgram(program, callback) {
 console.log('PROGRAM=' + JSON.stringify(program, null, 4));
 $.ajax({
        type: "POST",
        contentType: 'application/json',
        data: JSON.stringify(program),
        dataType: 'json',
        url: apiPath + 'run',
        success: function (data) {
            console.log('done', data);
            if (data.status == 'ok') {
                _.each(data.tracks, function(track, i) {
                    console.log(i + 1, track.title + ' ' + track.artist);
                });
            } else {
                console.log('error', data.status);
            }
            callback(data);
        }
    });
}
