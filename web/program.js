Program = function(inventory, name) {
    this.inventory = inventory;
    this.name = name;
    this.main = null;
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

        if (component.cls.type == 'source') {
            component.maxInputs = 0;
            component.minInputs = 0;
        } else if (component.cls.type == 'bool-filter') {
            component.maxInputs = 2;
            component.minInputs = 2;
        } else if (component.cls.type == 'multi-in-filter') {
            component.maxInputs = 20;
            component.minInputs = 1;
            component.source_list = [];
        } else {
            component.maxInputs = 1;
            component.minInputs = 1;
            component.source =  null;
        }
        return component;
    },

    hasMultiSource: function(component) {
        //return component.maxInputs > 1;
        return component.source_list != undefined;
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
            console.log('dup cname', name);
        }
        this.components[name] = c;
        return c;
    },

    removeComponent: function(name) {
        if (name in this.components) {
            delete this.components[name];
        }
    },

    addConnection: function(name1, name2, type) {
        console.log('ac', name1, name2);
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
     console.log('PROGRAM=' + json);
     $.ajax({
            type: "POST",
            contentType: 'application/json',
            data: json,
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
    },

    run: function(main, callback) {
        var that = this;
        this.main = main;

        var jsonProgram = this.toJson(this.main);
        this.extra.lastRun =  new Date().getTime(),
        console.log('json program', jsonProgram);
        this.postProgram(jsonProgram, function(data) {
            if (data) {
                that.extra.runs += 1;
            } else {
                that.extra.errors += 1;
            }
            that.save()
            console.log('run done', data);
            callback(data)
            localStorage.setItem('sp-last-run', getKey(that.name));
        });
    },

    save: function() {
        console.log('saving', this.name);
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
            console.log('extend', comp, '->', cc);
        });
        var json = JSON.stringify(obj, null, 4);
        console.log('SAVE ' + json);
        localStorage.setItem(getKey(this.name), json);
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

function loadProgram(inventory, key) {
    var program = null;
    var json = localStorage.getItem(key);
    if (json) {
        var sprog = JSON.parse(json);
        console.log('sprog', sprog);
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

