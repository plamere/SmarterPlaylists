Program = function(inventory, name) {
    this.inventory = inventory;
    this.name = name;
    this.main = null;
    this.max_tracks = 200;
    this.components = {}
    this.extra = { },
    this.trans = {
        needsSave: true,
    }
}

Program.prototype = {

    constructor: Program,

    createComponent: function(name, type, params, extra) {
        var component = {
            name: name,
            type: type,
            trans : {
                cls: this.inventory[type],
            },
            params: params,
            extra: extra,
            sources: {}
        }

        if (component.trans.cls.name == 'comment') {
            component.trans.maxInputs = 0;
            component.trans.maxOutputs = 0;
        } else if (component.trans.cls.type == 'source') {
            component.trans.maxInputs = 0;
            component.trans.minInputs = 0;
            component.trans.maxOutputs = 1;
        } else if (component.trans.cls.type == 'bool-filter') {
            component.trans.maxInputs = 2;
            component.trans.minInputs = 2;
            component.trans.maxOutputs = 1;
            component.sources.true_source = null;
            component.sources.false_source = null;
        } else if (component.trans.cls.type == 'multi-in-filter') {
            component.trans.maxInputs = 20;
            component.trans.minInputs = 1;
            component.trans.maxOutputs = 1;
            component.sources.source_list = [];
        } else {
            component.trans.maxInputs = 1;
            component.trans.minInputs = 1;
            component.trans.maxOutputs = 1;
            component.sources.source = null;
        }
        return component;
    },

    hasMultiSource: function(component) {
        //return component.maxInputs > 1;
        return component.sources.source_list != undefined;
    },

    getSources:function(c) {
        var sources = [];

        if (c.sources.source_list) {
            sources.push.apply(sources, c.sources.source_list)
        }
        if (c.sources.source) {
            sources.push(c.sources.source);
        }

        if (c.sources.true_source) {
            sources.push(c.sources.true_source);
        }

        if (c.sources.false_source) {
            sources.push(c.sources.false_source);
        }
        return sources;
    },


    addComponent: function(name, type, params, extra) {
        var c = this.createComponent(name, type, params, extra)
        if (name in this.components) {
            // console.log('dup cname', name);
        }
        this.components[name] = c;
        this.trans.needsSave = true;
        return c;
    },


    checkComponent: function(component) {
        var issues = [];
        _.each(component.trans.cls.params, function(param, pname) {
            var params = component.params;
            var sources = component.sources;
            if (!param.optional) {
                if (pname in params || pname in sources) {
                } else {
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
        this.trans.needsSave = true;
    },

    addConnection: function(name1, name2, type) {
        var c2 = this.components[name2];
        if (c2.trans.cls.type == 'bool-filter') {
            if (type == 0) {
                c2.sources.true_source = name1;
            } else {
                c2.sources.false_source = name1;
            }
        } else if (this.hasMultiSource(c2)) {
            c2.sources.source_list.push(name1);
        } else {
            c2.sources.source = name1;
        }
        this.trans.needsSave = true;
    },

    removeConnection: function(name1, name2) {
        var c2 = this.components[name2];

        if (c2.sources.true_source && c2.sources.true_source == name1) {
            c2.sources.true_source = null;
        }

        if (c2.sources.false_source && c2.sources.false_source == name1) {
            c2.sources.false_source = null;
        }

        if (this.hasMultiSource(c2)) {
            var idx = c2.sources.source_list.indexOf(name1);
            if (idx >= 0) {
                c2.sources.source_list.splice(idx, 1);
            }
        } else {
            if (c2.sources.source == name1) {
                c2.sources.source = null;
            }
        }
        this.trans.needsSave = true;
    },

    getComponent: function(name) {
        return this.components[name];
    },

    getComponents: function() {
        return this.components;
    },

    publishProgram: function(json, callback) {
     // console.log('publish PROGRAM=' + json);
     $.ajax({
            type: "POST",
            contentType: 'application/json',
            data: json,
            dataType: 'json',
            url: apiPath + 'publish',
            success: function (data) {
                callback(data);
            }
        });
    },

    save: function(callback) {
      var that = this;
      var data = {
        program: this.flatten(),
        auth_code: get_auth_code()
      };
      var json = JSON.stringify(data, null, 4);

      console.log('saving', this.pid, json);
      $.ajax({
            type: "POST",
            contentType: 'application/json',
            data: json,
            dataType: 'json',
            url: apiPath + 'save',
            success: function (data) {
                that.trans.needsSave = false;
                if (data.status == 'ok') {
                    that.pid = data.pid;
                }
                console.log(data);
                if (callback) {
                    callback(data);
                }
            },
            error: function(data) {
                if (callback) {
                    callback();
                }
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

    run: function(main, save, callback) {
        var that = this;
        this.main = main;

        this.saveIfNecessary(function(results) {
            if (results) {
                runProgram(results.pid,  save, function(data) {
                    callback(data)
                    localStorage.setItem('sp-last-run', getKey(that.name));
                });
            }
        });
    },

    saveIfNecessary: function(callback) {
        var that = this;
        if (this.trans.needsSave) {
            console.log('SAVED before run');
            this.save(callback);
        } else {
            console.log('NO Need for SAVE before run');
            var results = {
                status: 'ok',
                pid: this.pid
            }
            callback(results)
        }
    },

    publish: function(callback) {
    },

    flatten: function() {
        var obj = {};
        var obj = _.extendOwn(obj, this);
        obj.components = {};
        delete obj.inventory;
        delete obj.trans;

        _.each(this.components, function(comp, id) {
            var cc = {};
            cc = _.extendOwn(cc, comp);
            delete cc['trans'];
            obj.components[id] = cc;
        });
        return obj;
    },
}

function getKey(pname) {
    return 'sp-program:' + pname;
}

function loadMostRecentProgram(inventory) {
}


function removeProgram(pid, callback) {
     var data =  {
        pid:pid,
        auth_code: get_auth_code()
     };
     var json = JSON.stringify(data, null, 4);
     $.ajax({
            type: "POST",
            contentType: 'application/json',
            data: json,
            dataType: 'json',
            url: apiPath + 'delete',
            success: function (status) {
                console.log('removed', status);
                callback(status);
            },
            error: function() {
                console.log('not removed', status);
                callback(null);
            }
        });
}


function loadProgramFromJSON(inventory, sprog) {
    var program = new Program(inventory, sprog.name);
    program.name = sprog.name;
    program.main = sprog.main;
    program.max_tracks = sprog.max_tracks;
    program.extra = sprog.extra;
    program.pid = sprog.pid;
    program.trans.needsSave = false;
    _.each(sprog.components, function(comp, name) {
        program.addComponent(name, comp.type, comp.params, comp.extra);
    });

    _.each(sprog.components, function(comp, name) {
        if (comp.sources.true_source) {
            program.addConnection(comp.sources.true_source, name, 0);
        } 

        if (comp.sources.false_source) {
            program.addConnection(comp.sources.false_source, name, 1);
        } 

        if (comp.sources.source) {
            program.addConnection(comp.sources.source, name, 0);
        } else if (comp.sources.source_list) {
            _.each(comp.sources.source_list, function(source) {
                program.addConnection(source, name, 0);
            });
        }
    });
    return program;
}


function loadProgram(inventory, pid, callback) {
    $.getJSON(apiPath + "program",
        {
            auth_code: get_auth_code(),
            pid: pid
        }, 
        function(data) {
            console.log('loaded', data);
            if (data.status == 'ok') {
                var programJSON = data.program;
                var program = loadProgramFromJSON(inventory, programJSON);
                if (program) {
                    callback(program);
                } else {
                    error("Can't load program");
                    callback(null);
                }
            } else {
                error("Can't load program");
                callback(null);
            }
        }, 
        function() {
            error("Can't load program");
            callback(null);
        }
    );
}

function loadProgramDirectory(callback) {
    $.getJSON(apiPath + 'directory', 
        { 
            count:500,
            auth_code: get_auth_code
        },
        function(data) {
            console.log('data', data);
            callback(data);
        },
        function() {
            callback(null);
        }
    );
}

function loadInitialDirectory(inventory, callback) {
    loadProgramDirectory(callback);
}

function runProgram(pid, save, callback) {
     var program_post = {
        pid: pid,
        save: save,
        auth_code: get_auth_code()
     };
     var json = JSON.stringify(program_post, null, 4);
     console.log('PROGRAM=' + json);
     $.ajax({
            type: "POST",
            contentType: 'application/json',
            data: json,
            dataType: 'json',
            url: apiPath + 'run',
            success: function (data) {
                callback(data);
            },
            error: function() {
                callback();
            },
        });
}

function scheduleProgram(pid, callback) {
     var schedule_post = {
        auth_code: get_auth_code(),
        pid: pid,
        pid:pid,
        when: 0,
        delta: 100,
        total: 5
     };
     var json = JSON.stringify(schedule_post, null, 4);
     console.log('SCHEDULE=' + json);
     $.ajax({
            type: "POST",
            contentType: 'application/json',
            data: json,
            dataType: 'json',
            url: apiPath + 'schedule',
            success: function (data) {
                callback(data);
            },
            error: function() {
                callback();
            },
        });
}
