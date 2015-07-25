Program = function(inventory, name) {
    this.inventory = inventory;
    this.name = name;
    this.main = null;
    this.max_tracks = 200;
    this.components = {}
    this.extra = {
        createdOn: new Date().getTime(),
        lastRun: 0,
        runs: 0,
        errors: 0,
    }
}

Program.prototype = {

    constructor: Program,

    createComponent: function(name, type, params, extra) {
        var component = {
            name: name,
            type: type,
            cls: this.inventory[type],
            params: params,
            extra: extra,
        }

        if (component.cls.name == 'comment') {
            component.maxInputs = 0;
            component.maxOutputs = 0;
        } else if (component.cls.type == 'source') {
            component.maxInputs = 0;
            component.minInputs = 0;
            component.maxOutputs = 1;
        } else if (component.cls.type == 'bool-filter') {
            component.maxInputs = 2;
            component.minInputs = 2;
            component.maxOutputs = 1;
        } else if (component.cls.type == 'multi-in-filter') {
            component.maxInputs = 20;
            component.minInputs = 1;
            component.maxOutputs = 1;
            component.source_list = [];
        } else {
            component.maxInputs = 1;
            component.minInputs = 1;
            component.maxOutputs = 1;
            component.source =  null;
        }
        return component;
    },

    hasMultiSource: function(component) {
        //return component.maxInputs > 1;
        return component.source_list != undefined;
    },

    getSources:function(c) {
        var sources = [];

        if (c.source_list) {
            sources.push.apply(sources, c.source_list)
        }
        if (c.source) {
            sources.push(c.source);
        }

        if (c.true_source) {
            sources.push(c.true_source);
        }

        if (c.false_source) {
            sources.push(c.false_source);
        }
        return sources;
    },

    extract: function(c) {
        var out = { 
            _type: c.type
        }

        if (c.source) {
            out.source = c.source;
        }

        if (c.true_source) {
            out.true_source = c.true_source;
        }

        if (c.false_source) {
            out.false_source = c.false_source;
        }

        if (c.source_list) {
            out.source_list = c.source_list.slice();
        }
        _.extendOwn(out, c.params);
        return out;
    },

    toJson: function(rootComponentName)  {
        var that = this;
        var jsonProgram = {
            main : rootComponentName,
           max_tracks : this.max_tracks,
            components : {},
        }
        _.each(this.components, function(component) {
            var name = component.name;
            jsonProgram.components[name] = that.extract(component);
        });
        return JSON.stringify(jsonProgram, null, 4);
    },


    addComponent: function(name, type, params, extra) {
        var c = this.createComponent(name, type, params, extra)
        if (name in this.components) {
            // console.log('dup cname', name);
        }
        this.components[name] = c;
        return c;
    },


    checkComponent: function(component) {
        var issues = [];
        var ecomponent = this.extract(component);
        _.each(component.cls.params, function(param, pname) {
            if (!param.optional) {
                if (! (pname in ecomponent)) {
                    issues.push('missing required parameter: ' + pname);
                }
            }
        });
        return issues;
    },

    removeComponent: function(name) {
        if (name in this.components) {
            delete this.components[name];
        }
    },

    addConnection: function(name1, name2, type) {
        var c2 = this.components[name2];
        if (c2.cls.type == 'bool-filter') {
            if (type == 0) {
                c2.true_source = name1;
            } else {
                c2.false_source = name1;
            }
        } else if (this.hasMultiSource(c2)) {
            c2.source_list.push(name1);
        } else {
            c2.source = name1;
        }
    },

    removeConnection: function(name1, name2) {
        var c2 = this.components[name2];

        if (c2.true_source && c2.true_source == name1) {
            c2.true_source = null;
        }

        if (c2.false_source && c2.false_source == name1) {
            c2.false_source = null;
        }

        if (this.hasMultiSource(c2)) {
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
        return this.components[name];
    },

    getComponents: function() {
        return this.components;
    },

    postProgram: function(json, callback) {
     // console.log('PROGRAM=' + json);
     $.ajax({
            type: "POST",
            contentType: 'application/json',
            data: json,
            dataType: 'json',
            url: apiPath + 'run',
            success: function (data) {
                if (data.status == 'ok') {
                    _.each(data.tracks, function(track, i) {
                        // console.log(i + 1, track.title + ' ' + track.artist);
                    });
                } else {
                    // console.log('error', data.status);
                }
                callback(data);
            }
        });
    },

    findActiveComponents: function(c, active) {
        var that = this;
        if (! (c.name in active)) {
            active[c.name] = c;
            var sources = this.getSources(c);
            _.each(sources, function(source) {
                var sc = that.components[source];
                that.findActiveComponents(sc, active);
            });
        }
    },

    getActiveComponents: function(main) {
        var active = {}
        var mainComponent = this.components[main];
        this.findActiveComponents(mainComponent, active);
        return active;
    },

    check: function(main) {
        var that = this;
        var issues = [];
        var components = this.getActiveComponents(main);
        _.each(components, function(component) {
            var cissues = that.checkComponent(component);
            _.each(cissues, function(cissue) {
                var issue = {
                    component:component.name,
                    message: cissue
                }
                issues.push(issue);
            });
        });
        return issues;
    },

    run: function(main, callback) {
        var that = this;
        this.main = main;
        this.extra.lastRun =  new Date().getTime();

        var jsonProgram = this.toJson(this.main);
        this.postProgram(jsonProgram, function(data) {
            if (data) {
                that.extra.runs += 1;
            } else {
                that.extra.errors += 1;
            }
            callback(data)
            localStorage.setItem('sp-last-run', getKey(that.name));
        });
    },

    save: function() {
        this.extra.lastRun =  new Date().getTime();
        var obj = {
            name:this.name,
            main:this.main,
            components:{},
            extra:this.extra
        }

        _.each(this.components, function(comp, id) {
            var cc = {};
            cc = _.extendOwn(cc, comp);
            delete cc['cls'];
            obj.components[id] = cc;
        });
        var json = JSON.stringify(obj, null, 4);
        localStorage.setItem(getKey(this.name), json);
        return json;
    }
}

function getKey(pname) {
    return 'sp-program:' + pname;
}

function loadMostRecentProgram(inventory) {
    var last = localStorage.getItem('sp-last-run');
    if (last) {
        return loadProgram(inventory, last);
    } else {
        return null;
    }
}


function removeProgram(name) {
    localStorage.removeItem(getKey(name));
}


function loadProgramFromJSON(inventory, sprog) {
    var program = new Program(inventory, sprog.name);
    program.name = sprog.name;
    program.main = sprog.main;
    program.extra = sprog.extra;
    _.each(sprog.components, function(comp, name) {
        program.addComponent(name, comp.type, comp.params, comp.extra);
    });

    _.each(sprog.components, function(comp, name) {
        if (comp.true_source) {
            program.addConnection(comp.true_source, name, 0);
        } 

        if (comp.false_source) {
            program.addConnection(comp.false_source, name, 1);
        } 

        if (comp.source) {
            program.addConnection(comp.source, name, 0);
        } else if (comp.source_list) {
            _.each(comp.source_list, function(source) {
                program.addConnection(source, name, 0);
            });
        }
    });
    return program;
}


function loadProgram(inventory, key) {
    var program = null;
    var json = localStorage.getItem(key);
    var sprog = JSON.parse(json);
    if (sprog) {
        program = loadProgramFromJSON(inventory, sprog);
    }
    return program;
}

function loadDirectory(inventory) {
    var dir = [];
    for (var i = 0; i < localStorage.length; i++) {
        var key = localStorage.key(i);
        if (key.indexOf('sp-program:') == 0) {
            dir.push(loadProgram(inventory, key));
        }
    }
    return dir;
}

function loadInitialDirectory(inventory, callback) {
    var visited = localStorage.getItem('sp-has-visited');
    if (!visited) {
        localStorage.setItem('sp-has-visited', 'visited');
        $.getJSON('examples.js?v1').then(
            function(data) {
                var dir = [];
                _.each(data, function(prog) {
                    var program = loadProgramFromJSON(inventory, prog);
                    program.save();
                    dir.push(program);
                });
                callback(dir);
            },

            function() {
            }
        );
    } else {
        callback(loadDirectory(inventory));
    }
}

