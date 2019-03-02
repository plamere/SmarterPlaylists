Program = function(inventory, name) {
    this.inventory = inventory;
    this.name = name;
    this.main = null;
    this.description = "my description";
    this.max_tracks = 1000;
    this.components = {}
    this.extra = { },
    this.trans = {
        needsSave: true,
    }
    this.portTypes = ['green', 'blue', 'red', 'orange'];
}


Program.prototype = {

    constructor: Program,

    createComponent: function(name, type, params, extra) {
        console.log("cc", name, type, params, extra);
        if (!(type in this.inventory)) {
            console.log("missing type", type, "converting to El Scorcho");
            type = "TrackSourceByName";
            params = {title: "el scorcho"};
        }

        var component = {
            name: name,
            type: type,
            trans : { // this is transient stuff, not shipped over the wire
                cls: this.inventory[type],
                ports: {} // describes the various ports
            },
            params: params,
            extra: extra,
            sources: {}
        }

        // by default, all ports are closed
        component.trans.maxOutputs = 1;
        _.each(this.portTypes, function(port) {
            component.trans.ports[port] = {name:null, maxInputs:0};
        });

        // console.log('cc', component);

        if ('max_outputs' in component.trans.cls) {
          component.trans.maxOutputs = component.trans.cls.max_outputs;
        }
        _.each(this.portTypes, function(port) {
            var portInfo = getPortInfo(component, port);
            if (portInfo) {
              component.trans.ports[port] = portInfo;
              if (portInfo.maxInputs > 0) {
                  if (portInfo.maxInputs == 1) {
                    component.sources[portInfo.name] = null;
                  } else {
                    component.sources[portInfo.name] = [];
                  }
              }
            }
        });
        return component;
    },

    getSources:function(c) {
        var sources = [];
        _.each(c.sources, function(src) {
            if (Array.isArray(src)) {
              sources.push.apply(sources, src);
            } else {
              sources.push(src);
            }
        });
        return sources;
    },


    addComponent: function(name, type, params, extra) {
        var c = this.createComponent(name, type, params, extra)
        if (name in this.components) {
            // console.log('dup cname', name);
        }
        if (c) {
            this.components[name] = c;
            this.trans.needsSave = true;
        }
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
        if (type in c2.trans.ports) {
            var port = c2.trans.ports[type];
            if (port.maxInputs == 1) {
              c2.sources[port.name] = name1
            } else if (port.maxInputs > 1) {
              c2.sources[port.name].push(name1);
              while (c2.sources[port.name].length > port.maxInputs) {
                c2.sources[port.name].shift();
              }
            } else {
                alert("no inputs allowed for " + name2);
            }
        } else {
              alert("no inputs allowed for that type of port on " + name2);
        }
        this.trans.needsSave = true;
    },

    removeConnection: function(name1, name2) {
        var c2 = this.components[name2];
        _.each(c2.sources, function(src, name) {
            if (Array.isArray(src)) {
              var idx = src.indexOf(name1);
              if (idx >= 0) {
                  src.splice(idx, 1);
              }
            } else {
                if (src == name1) {
                  c2.sources[name] = null;
                }
            }
        });
        this.trans.needsSave = true;
    },

    getComponent: function(name) {
        return this.components[name];
    },

    getComponents: function() {
        return this.components;
    },

    publishProgram: function(json, callback) {
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
            this.save(callback);
        } else {
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
        var obj = _.extend(obj, this);
        obj.components = {};
        delete obj.inventory;
        delete obj.trans;
        delete obj.portTypes;

        _.each(this.components, function(comp, id) {
            var cc = {};
            cc = _.extend(cc, comp);
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
                callback(status);
            },
            error: function() {
                callback(null);
            }
        });
}

function loadProgramFromJSON(inventory, sprog) {
    var program = new Program(inventory, sprog.name);
    program = _.extend(program, sprog);
    program.trans.needsSave = false;
    program.components = {}
    _.each(sprog.components, function(comp, name) {
        program.addComponent(name, comp.type, comp.params, comp.extra);
    });

    _.each(sprog.components, function(comp, componentName) {
        _.each(comp.sources, function(source, connectionName) {
            var cls = inventory[comp.type];
            var ctype = getConnectionType(cls, connectionName);
            if (Array.isArray(source)) {
                _.each(source, function(src) {
                    program.addConnection(src, componentName, ctype);
                });
            } else {
                if (source) {
                  program.addConnection(source, componentName, ctype);
                }
            }
        });
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

function loadSharedProgram(inventory, pid, callback) {
    var path = apiPath + 'shared';
    $.getJSON(path, { pid:pid}).then(
        function(data) {
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

function loadProgramInfo(pid, callback) {
    $.getJSON(apiPath + "program",
        {
            auth_code: get_auth_code(),
            pid: pid
        },
        function(data) {
            if (data.status == 'ok') {
                if (data.program) {
                    callback(data.program);
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

function loadSharedProgramInfo(pid, callback) {
    $.getJSON(apiPath + "shared_info",
        {
            auth_code: get_auth_code(),
            pid: pid
        },
        function(data) {
            if (data.status == 'ok') {
                callback(data.info);
            } else {
                error("Can't load shared program info");
                callback(null);
            }
        },
        function() {
            error("Can't load shared program");
            callback(null);
        }
    );
}

function loadProgramDirectory(callback) {
    $.getJSON(apiPath + 'directory',
        {
            count:500,
            auth_code: get_auth_code()
        },
        function(data) {
            checkForBadUser(data);
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

function loadImports(callback) {
    $.getJSON(apiPath + 'imports',
        {
            count:500,
            auth_code: get_auth_code()
        },
        function(data) {
            checkForBadUser(data);
            callback(data);
        },
        function() {
            callback(null);
        }
    );
}

function loadExamples(callback) {
    $.getJSON(apiPath + 'examples',
        {
            auth_code: get_auth_code()
        },
        function(data) {
            checkForBadUser(data);
            callback(data);
        },
        function() {
            callback(null);
        }
    );
}

function runProgram(pid, save, callback) {
     var program_post = {
        pid: pid,
        save: save,
        auth_code: get_auth_code()
     };
     var json = JSON.stringify(program_post, null, 4);
     // console.log('PROGRAM=' + json);
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

function scheduleProgram(pid, when, delta, total, callback) {
     var schedule_post = {
        auth_code: get_auth_code(),
        pid: pid,
        when: when,
        delta: delta,
        total: total
     };
     var json = JSON.stringify(schedule_post, null, 4);
     // console.log('SCHEDULE=' + json);
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

function copyProgram(pid, callback) {
     var post = {
        auth_code: get_auth_code(),
        pid: pid,
     };
     var json = JSON.stringify(post, null, 4);
     // console.log('COPY=' + json);
     $.ajax({
            type: "POST",
            contentType: 'application/json',
            data: json,
            dataType: 'json',
            url: apiPath + 'copy',
            success: function (data) {
                callback(data);
            },
            error: function() {
                callback();
            },
        });
}

function importProgram(pid, callback) {
     var post = {
        auth_code: get_auth_code(),
        pid: pid,
     };
     var json = JSON.stringify(post, null, 4);
     // console.log('IMPORT=' + json);
     $.ajax({
            type: "POST",
            contentType: 'application/json',
            data: json,
            dataType: 'json',
            url: apiPath + 'import',
            success: function (data) {
                callback(data);
            },
            error: function() {
                callback();
            },
        });
}

function shareProgram(pid, state, callback) {
     var post = {
        auth_code: get_auth_code(),
        pid: pid,
        share: state
     };
     var json = JSON.stringify(post, null, 4);
     // console.log('SHARE=' + json);
     $.ajax({
            type: "POST",
            contentType: 'application/json',
            data: json,
            dataType: 'json',
            url: apiPath + 'publish',
            success: function (data) {
                callback(data);
            },
            error: function() {
                callback();
            },
        });
}

function getPortInfo(component, color) {
    var matches = 0;

    var portInfo = {
        maxInputs:0,
        name:null
    };
    _.each(component.trans.cls.params, function(param, name) {
        if (param.type == 'port' && color == param.port) {
            portInfo.name = name;
            portInfo.maxInputs = param.max_inputs;
            matches += 1;
        }
    });
    if (matches > 1) {
      alert("too many " + color + " ports for " + name);
    }
    return portInfo;
}


function getConnectionType(cls, connectionName) {
    var connectionType = null;
    var params = cls.params;
    if (connectionName in params) {
        if ('port' in params[connectionName]) {
          connectionType = params[connectionName].port;
        }
    }
    return connectionType;
}
