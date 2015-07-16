var createEditor = function(canvasElem, inventory, types) {
    var spotifyGreen = '#1ED760';
    var spotifyRed = '#D71E60';
    var tileWidth = 100;
    var tileHeight = 60;
    var textXOffset = tileWidth / 2;
    var textYOffset = 30;
    var xMargin = 40;
    var yMargin = 80;
    var sources = []
    var filters = []
    var conditionals = []
    var tWidth = (tileWidth + xMargin);
    var widgetsPerRow = 0;

    var widgetCount = 0;
    var connections = [];
    var controlled = false;
    var shifted = false;
    var program = new Program(inventory, 'my program');
    var previousComponent = null;
    var curSelected = null;
    var altSelected = null;
    var paper = null;
    var canvasHasFocus = true;
    var CT_NORMAL = 0;
    var CT_SHIFTED = 1;

    var nameToRect = {}

    console.log('create editor', types);
    function initPaper() {
        var top = 100;
        var w = $(window).width();
        var h = $(window).height() - top;

        console.log('width/height', w,h);
        paper = Raphael(canvasElem, w, h);
        paper.canvas.className += ' raphael-canvas';
        paper.canvas.baseVal += ' raphael-canvas';
        widgetsPerRow = Math.floor(paper.canvas.offsetWidth / tWidth);

        (function($,sr){
         
          // debouncing function from John Hann
          // http://unscriptable.com/index.php/2009/03/20/debouncing-javascript-methods/
          var debounce = function (func, threshold, execAsap) {
              var timeout;
         
              return function debounced () {
                  var obj = this, args = arguments;
                  function delayed () {
                      if (!execAsap)
                          func.apply(obj, args);
                      timeout = null; 
                  };
         
                  if (timeout)
                      clearTimeout(timeout);
                  else if (execAsap)
                      func.apply(obj, args);
         
                  timeout = setTimeout(delayed, threshold || 100); 
              };
          }
            // smartresize 
            jQuery.fn[sr] = function(fn){  return fn ? this.bind('resize', debounce(fn)) : this.trigger(sr); };
         
        })(jQuery,'smartresize');

        // usage:
        $(window).smartresize(function(){  
            refreshLayout(true);
        });
    }

    function refreshLayout(state) {
        var workspace = $("#workspace");
        if (workspace.is(':visible')) {
            var w = workspace.width();
            var h = workspace.height();
            paper.setSize(w, h);
            console.log('refresh', w, h);
        }
    }

    function canvasFocus(state) {
        canvasHasFocus = state;
    }

    function getConnType() {
        return shifted ? CT_SHIFTED : CT_NORMAL;
    }

    var dragger = function () {
        var rect = this;
        if (this.parent) {
            rect = this.parent;
        }

        rect.ox = rect.type == "rect" ? rect.attr("x") : rect.attr("cx");
        rect.oy = rect.type == "rect" ? rect.attr("y") : rect.attr("cy");
        // rect.animate({"fill-opacity": .2}, 500);
    }

    function deleteCur() {
        if (curSelected) {
            deleteComponent(curSelected);
            curSelected = null;
        }
    }

    function connectComponents() {
        if (altSelected && curSelected && altSelected != curSelected) {
            connectComponent(altSelected, curSelected, getConnType());
        }
    }

    function deleteComponent(comp) {
        disconnectComponent(comp);
        program.removeComponent(comp.name);
        comp.label.remove();
        comp.remove();
    }

    function moveTo(rect, x, y) {
        var att = rect.type == "rect" ? 
            {x: x, y: y} : 
            {cx: x, cy: y};

        rect.attr(att);
        rect.component.extra.x = x;
        rect.component.extra.y = y;

        if (rect.label) {
            var lattr = { x: x + textXOffset, y: y + textYOffset }
            rect.label.attr(lattr);
        }
    }

    function convertType(type, val)  {
        var typeConverters = {
            'string': function(val) {
                return val;
            },
            'number': function(val) {
                if (val.indexOf('.') >=0) {
                    return parseFloat(val);
                } else {
                    return parseInt(val);
                }
            },
            'bool': function(val) {
                return val.toLowerCase() == 'true';
            }
        }

        if (type in typeConverters) {
            return typeConverters[type](val);
        } else {
            return val;
        }
    }

    function keydown(evt) {


        if (!canvasHasFocus) {
            return;
        }

        if ($(evt.target).is('input')) {
            console.log('is input');
            return;
        }

        console.log('key', evt.which, evt);
        if (evt.which == 17) {
            controlled = true;
        }

        if (evt.which == 16) {
            shifted = true;
        }

        if (evt.which == 8) {
            evt.preventDefault();
            deleteCur();
        }

        if (evt.which == 32) {
            evt.preventDefault();
            connectComponents()
        }
    }

    function keyup(evt) {
        if (evt.which == 17) {
            controlled = false;
        }
        if (evt.which == 16) {
            shifted = false;
        }
    }

    
   var  move = function (dx, dy) {
        var rect = this;
        if (this.parent) {
            rect = this.parent;
        }

        var newX = rect.ox + dx;
        var newY = rect.oy + dy;

        moveTo(rect, newX, newY);

        for (var i = connections.length; i--;) {
            paper.connection(connections[i]);
        }
    };

    var up = function () {
        var rect = this;
        if (this.parent) {
            rect = this.parent;
        }
        // rect.animate({"fill-opacity": 0}, 500);
    };

    function selectRect(rect, state) {
        if (state) {
            rect.attr({'stroke-width' : 6});
        } else {
            curSelected.attr({'stroke-width' : 1});
        }
        console.log(rect.component.cls.color);
    }

    function markComponentWithError(name, msg) {
        var rect = nameToRect[name];
        rect.attr({ stroke: spotifyRed});
        rect.hasError = true;
        rect.errorMessage = msg;
    }

    function clearComponentErrors() {
        $("#errors").empty(200);
        _.each(nameToRect, function(rect, name) {
            if (rect.hasError) {
                rect.hasError = false;
                rect.attr({ stroke: "#000000"});
            }
        });
    }

    function altSelectRect(rect, state) {
        if (state) {
            rect.attr({'stroke-dasharray' : ['-']});
            rect.attr({'stroke-width' : 6});
        } else {
            rect.attr({'stroke-dasharray' : null});
            rect.attr({'stroke-width' : 1});
        }
    }

    var select = function() {
        var rect = this;
        if (this.parent) {
            rect = this.parent;
        }
        
        if (shifted) {
            if (altSelected) {
                altSelectRect(altSelected, false);
            }
            altSelected = rect;
            if (curSelected == altSelected) {
                selectRect(curSelected, false);
                curSelected = null;
            }
            altSelectRect(altSelected, true);
        } else {
            if (curSelected) {
                if (altSelected) {
                    altSelectRect(altSelected, false);
                }
                altSelected = curSelected;
                altSelectRect(altSelected, true);
            }
            if (curSelected != null) {
                selectRect(curSelected, false);
            }
            curSelected = rect;

            if (curSelected == altSelected) {
                altSelectRect(altSelected, false);
                altSelected = null;
            }
            selectRect(curSelected, true);
        }
    }
    var edit = function() {
        var rect = this;
        if (this.parent) {
            rect = this.parent;
        }

        canvasFocus(false);
        var component = rect.component;

        $("#edit-modal .modal-title").text(component.cls.display);
        $("#edit-modal .description").text(component.cls.description);
        if (component.cls.help) {
            $("#edit-modal .help").html(component.cls.help);
        } else {
            $("#edit-modal .help").text("");
        }
        $("#edit-modal .error").empty();
        if (rect.hasError) {
            $("#edit-modal .error").append($("<h3>").text('Errors'));
            $("#edit-modal .error").append($("<span>").text(rect.errorMessage));
        } 

        var curParams = {};

        function addParam(pdiv, name, param) {
            var div = $("<div class='form-group'>");

            if (false && 'default' in param) {
                curParams[name] = param['default'];
            }

            var opt = param.optional ? "" : " (required) ";
            if (param.type in types) {
                var label =  $('<label for="' + name + '">').text(name + opt);
                label.attr('title', param.description);
                label.addClass("edit-param-label");
                var val = component.params[name] ?
                          component.params[name] : param['default'];
                var sel = $("<select>");
                _.each(types[param.type], function(type) {
                    var opt = $("<option>");
                    if (type.value == val) {
                        opt.prop('selected', true);
                    }
                    opt.val(type.value);
                    opt.text(type.name);
                    sel.append(opt);
                });
                sel.attr('id', name);

                sel.on('change', function() {
                    curParams[name] = convertType(param.stype, sel.val());
                    console.log('change', curParams);
                });
                div.append(label);
                div.append(sel);
            }
            else if (param.type  == 'string' || param.type == 'uri') {

                var label =  $('<label for="' + name + '">').text(name + opt);
                label.attr('title', param.description);
                label.addClass("edit-param-label");
                var val = component.params[name] ?
                          component.params[name] : param['default'];
                var inp = $("<input class='form-control'>").val(val);
                inp.attr('id', name);

                inp.on('change', function() {
                    curParams[name] = inp.val();
                });


                div.append(label);
                div.append(inp);
            }
            if (param.type  == 'uri_list') {
                var label =  $('<label for="' + name + '">').text(name + opt);
                label.attr('title', param.description);
                label.addClass("edit-param-label");
                var val = component.params[name];
                if (val) {
                    val = val.join(',')
                }
                var inp = $("<input class='form-control'>").val(val);
                inp.attr('id', name);

                inp.on('change', function() {
                    curParams[name] = inp.val().split(',');
                });
                div.append(label);
                div.append(inp);
            } else if (param.type  == 'string_list') {
                var label =  $('<label for="' + name + '">').text(name + opt);
                label.attr('title', param.description);
                label.addClass("edit-param-label");
                var val = component.params[name];
                if (val) {
                    val = val.join(',')
                }
                var inp = $("<input class='form-control'>").val(val);
                inp.attr('id', name);

                inp.on('change', function() {
                    //curParams[name] = inp.val().split(',');
                    curParams[name] = inp.val().match(/(?=\S)[^,]+?(?=\s*(,|$))/g);
                });
                div.append(label);
                div.append(inp);
            }
            else if (param.type  == 'number') {
                var label =  $('<label for="' + name + '">').text(name + opt);
                label.addClass("edit-param-label");
                label.attr('title', param.description);
                var val = component.params[name] ?
                          component.params[name] : param['default'];
                var inp = $("<input class='form-control'>").val(val);
                inp.attr('id', name);

                inp.on('change', function() {
                    var val = inp.val();

                    if (val.indexOf('.')) {
                        curParams[name] = parseFloat(inp.val());
                    } else {
                        curParams[name] = parseInt(inp.val());
                    }
                });
                div.append(label);
                div.append(inp);
            }
            else if (param.type  == 'bool') {
                var label = $('<label class="edit-param-label">');
                var val = component.params[name];
                var inp = $("<input type='checkbox' class='param-checkbox'>");
                inp.attr('id', name);
                inp.prop('checked', val);
                inp.on('change', function() {
                    var state = $(inp).is(':checked');
                    curParams[name] = state;
                    console.log('bool', name, state);
                });
                label.text(name);
                label.attr('title', param.description);
                div.append(label);
                div.append(inp);
            }
            pdiv.append(div);
        } 

        
        var pdiv = $("#edit-modal .params");
        pdiv.empty();
        _.each(component.cls.params, function(param, name) {
            if (name != 'source') {
                addParam(pdiv, name, param);
            }
        });

        $('#edit-modal').modal({})


        $('#edit-modal').on('hidden.bs.modal', function () {
            canvasFocus(true);
        });

        $("#edit-modal .save").on('click', function() {
            _.each(curParams, function(val, name) {
                component.params[name] = val;
            });
            console.log('save', component.params);
            renameComponent(rect);
        });

    }

    function renameComponent(rect) {
        console.log('rc', rect);
        var title = rect.component.cls.title || rect.component.cls.display;
        title = makeSubs(title, rect.component);
        addLabel(rect, title);
        // rect.label.attr('text', title + '\n' + 'more lines');
    }

    function findTypeName(key, type) {
            console.log('findTypeName', key, type);
        var name = '?';
        _.each(type, function(t) {
            if (key == t.value) {
                console.log('findTypeName', key, type, t);
                name =  t.name;
            }
        });
        return name;
    }

    function makeSubs(title, component) {
        var out = []

        function makeSub(word, component) {
            var key  = word.replace('$', '');
            if (key in component.params) {
                var keyType = component.cls.params[key].type;
                console.log('makesubs', keyType, types);
                if (keyType in types) {
                    key = findTypeName(component.params[key], types[keyType]);
                    return key;
                } else if (keyType == 'bool') {
                    if (component.params[key]) {
                        return key;
                    } else {
                        return null;
                    }
                } else {
                    return component.params[key];
                }
            } else {
                return '?'
                //return word;
            }
        }
        _.each(title.split(' '), function(word, i) {
            if (word.indexOf('$') == 0) {
                word = makeSub(word, component);
            }
            if (word) {
                out.push(word);
            }
        });

        return out.join(' ');
    }



    // lelf over from testing
    function addDraggableObjects() {
            shapes = [  paper.ellipse(190, 100, 30, 20),
                        paper.rect(290, 80, 60, 40, 10),
                        paper.rect(290, 180, 60, 40, 2),
                        paper.rect(240, 140, 60, 40, 2),
                        paper.ellipse(450, 100, 20, 20)
                    ];
        for (var i = 0, ii = shapes.length; i < ii; i++) {
            var color = Raphael.getColor();
            shapes[i].attr({fill: color, stroke: color, "fill-opacity": 0, "stroke-width": 2, cursor: "move"});
            shapes[i].drag(move, dragger, up);
        }
        connections.push(paper.connection(shapes[0], shapes[1], "#fff"));
        connections.push(paper.connection(shapes[1], shapes[2], "#fff", "#fff|5"));
        connections.push(paper.connection(shapes[1], shapes[3], "#000", "#fff"));
    }


    function connectComponent(source, dest, connType) {
        if (dest.component.maxInputs == 0) {
            return;
        }

        if (dest.component.cls.type != 'bool-filter') {
            connType = CT_NORMAL;
        }

        if (dest.component.maxInputs == 1) {
            disconnectInputs(dest);
        } else if (dest.component.maxInputs == 2) {
            disconnectInput(dest, connType);
        }

        disconnectOutputs(source);

        var edge = addVisualConnection(source, dest, connType);
        program.addConnection(source.name, dest.name, connType);
    }

    function addVisualConnection(srcRect, destRect, connType) {
        var color = connType == CT_NORMAL ? spotifyGreen : spotifyRed;
        var edge = paper.connection(srcRect, destRect, color);
        connections.push(edge);
        edge.source = srcRect;
        edge.dest = destRect;
        edge.type = connType;
        srcRect.outEdges[destRect.name] = edge;
        destRect.inEdges[srcRect.name] = edge;
        return edge;
    }


    function removeEdge(edge) {
        program.removeConnection(edge.source.name, edge.dest.name);
        delete edge.source.outEdges[edge.dest.name]
        delete edge.dest.inEdges[edge.source.name]
        edge.remove();
        var idx = connections.indexOf(edge);
        if (idx >= 0) {
            connections.splice(idx, 1);
        }
    }

    function disconnectComponent(comp) {
        disconnectInputs(comp);
        disconnectOutputs(comp);
    }

    function disconnectInputs(comp) {
        _.each(comp.inEdges, function(edge, destName) {
            removeEdge(edge);
        });
    }

    function disconnectInput(comp, compType) {
        _.each(comp.inEdges, function(edge, destName) {
            if (edge.type == compType) {
                removeEdge(edge);
            }
        });
    }

    function disconnectOutputs(comp) {
        _.each(comp.outEdges, function(edge, destName) {
            removeEdge(edge);
        });
    }


    function nextComponentName(component) {
        while (true) {
            widgetCount++;
            var nextName =  component.name + '-' + widgetCount
            if (! (nextName in nameToRect) ) {
                return nextName;
            }
        }
    }


    function addNewComponent(componentType, comp) {
        var col = widgetCount * 12;
        var row = widgetCount * 12;
        var xpos = xMargin + col;
        var ypos = yMargin + row;

        var rect = paper.rect(xpos, ypos, tileWidth, tileHeight, 4);
        var color = Raphael.getColor();

        color = componentType.color;

        rect.attr({
            fill: "#ffffff", 
            stroke: color, 
            "stroke-width": 2, 
            cursor: "move",
            });


        rect.label = paper.text(xpos + textXOffset, 
            ypos + textYOffset, componentType.name);
        rect.label.parent = rect;


        rect.label.attr({
            fill: color, 
            stroke: color, 
            cursor: "move",
            "stroke-width": 0,
            "font-family":"Arial",
            "font-size": 12,
            "font-weight": 'lighter'
        });

        //addLabel(rect, componentType.name);

        rect.inEdges = {};
        rect.outEdges = {};
        rect.drag(move, dragger, up);
        rect.label.drag(move, dragger, up);

        rect.dblclick(edit);
        rect.label.dblclick(edit);

        rect.click(select);
        rect.label.click(select);

        if (comp) {
            rect.component = comp;
            rect.name = comp.name;
            moveTo(rect, comp.extra.x, comp.extra.y);
        } else {
            rect.name = nextComponentName(componentType);
            rect.component = program.addComponent(rect.name, componentType.name, {}, {});
            _.each(rect.component.cls.params, function(param, name) {
                if ('default' in param) {
                    rect.component.params[name] = param['default'];
                } else if (param.type == 'bool') {
                    rect.component.params[name] = false;
                }
            });
            moveTo(rect, xpos, ypos);
        }
        renameComponent(rect);


        // Set component param defaults and rename
        // component
        nameToRect[rect.name] = rect;
        return rect;
    }

    function addLabel(rect, text) {
        var margin = 10;
        var width = rect.attr('width') - margin;
        var words = text.split(" ");

        var out = "";

        _.each(words, function(word) {
            rect.label.attr({"text": out + " " + word});
            if (rect.label.getBBox().width >= width) {
                out += '\n';
            } else {
                out += '  ';
            }
            out += word;
        });
        rect.label.attr({"text": out });
    }

    function isConnected(comp) {
        return (_.keys(comp.outEdges).length > 0);
    }

    function addComponent(elem, comp) {
        var button = $("<li>")
            .text(comp.display)
            .attr('title', comp.description);
        elem.append(button);
        button.on('click', function() {
            var newComponent = addNewComponent(comp);
            if (previousComponent && !isConnected(previousComponent)) {
                connectComponent(previousComponent,
                    newComponent,getConnType());
            }
            previousComponent = newComponent;
            select.apply(newComponent);
        });
    }

    function showInventoryUI() {
        var sourceList = $("#sources");

        sources.sort(function(a,b) {
            return a.display.localeCompare(b.display);
        });
        _.each(sources, function(source) {
            addComponent(sourceList, source);
        });

        filters.sort(function(a,b) {
            return a.display.localeCompare(b.display);
        });
        var filterList = $("#filters");
        _.each(filters, function(filter) {
            addComponent(filterList, filter);
        });

        conditionals.sort(function(a,b) {
            return a.display.localeCompare(b.display);
        });
        var conditionalList = $("#conditionals");
        _.each(conditionals, function(conditional) {
            addComponent(conditionalList, conditional);
        });
    }

    function sortComponents() {
        _.each(inventory, function(component, name) {
            if (component.type == 'filter') {
                filters.push(component);
            }
            else if (component.type == 'multi-in-filter') {
                filters.push(component);
            } else if (component.type == 'bool-filter') {
                conditionals.push(component);
            }
            else if (component.type == 'source') {
                sources.push(component);
            } 
            else {
                alert('unsupported ' + component.type);
            }
        });
    }

    function setRunning(state) {
        if (state) {
            $("#running-state").addClass('text-info');
            $("#running-state").text('running');
            $("#run-button").prop("disabled", true);

        } else {
            $("#running-state").text('');
            $("#run-button").prop("disabled", false);
        }
    }

    function addControls() {
        var runButton = $("#run-button");
        runButton.on('click', function() {
            var title = $("#program-name").text();
            var saveToSpotify = $('#save-playlist').is(':checked');
            if (program.name != title) {
                program.name = title;
                program.extra.uri = null;
            }

            program.save();
            clearComponentErrors();
            if (curSelected) {
                var main = curSelected.name;
                var issues = program.check(main);
                console.log('check issues', issues);
                if (issues.length > 0) {
                    _.each(issues, function(issue) {
                        if (issue.component) {
                            error(issue.component + ": " + issue.message);
                            markComponentWithError(issue.component, issue.message);
                        } else {
                            error(issue.message);
                        }
                    });
                } else {
                    setRunning(true);
                    program.run(main, function(data) {
                        setRunning(false);
                        if (data) {
                            if (data.status == 'ok') {
                                showPlaylist(program.name, data);
                                if (saveToSpotify) {
                                    savePlaylist(program, data);
                                }
                            } else {
                                console.log(data);
                                error(data.message);
                                if (data.component) {
                                    markComponentWithError(data.component, data.message);
                                }
                            }
                        }
                    });
                }
            } else {
                alert("select a component to run");
            }
        });


        var saveButton = $("#save-button");
        saveButton.on('click', function() {
            var title = $("#program-name").text();
            program.name = title;
            program.save();
            info("Saved " + title);
        });
    }


    function initUI() {
        addControls();
        showInventoryUI();
    }

    function getNextColor() {
        var badColors = ['#0c00ff'];
        while (true) {
            color = Raphael.getColor(.1);
            if (badColors.indexOf(color) == -1) {
                return color;
            }
        }

        return "#000000";
    }

    function assignColorsToInventory() {
        _.each(inventory, function(component, name) {
            component.color = getNextColor();
        });
    }

    function initEditor() {
        initPaper()
        sortComponents();
        assignColorsToInventory();
        initUI();
        var elemName = "#" + canvasElem;
        $(document).keydown(keydown);
        $(document).keyup(keyup);

        $(window).bind('storage', function (e) {
            var evt = e.originalEvent;
            if (evt.key == 'playlist-save-status') {
                var obj = JSON.parse(evt.newValue);
                if (program.name == obj.name) {
                    program.extra.uri = obj.uri;
                    program.save();
                }
            }
        });

        // TODO:  Instead of always saving programs, we might add
        //  and onbeforeunload event that will save just the dirty ones
        //  before we exit.
        $('#program-name').editable({
            type: 'text',
            mode: 'inline',
            title: 'Enter Program Name',
            placement: 'bottom',
            showbuttons: false,
            inputclass: 'program-input',
            success: function(response, newValue) {
                program.name = newValue;
                program.extra.runs = 0;
                program.extra.errors = 0;
                program.extra.uri = null;
                program.save();
             }
        });
    }

    function setProgramName(name) {
    }

    function initNewProgram(newProgram) {
        widgetCount = 0;
        paper.clear();
        connections = [];
        nameToRect = {};
        program = newProgram;
        previousComponent = null;
        curSelected = null;
        altSelected = null;
        canvasFocus(true);
    }

    initEditor();
    return {    
        load:function(newProgram) {
            initNewProgram(newProgram);

            _.each(program.components, function(comp, id) {
                addNewComponent(comp.cls, comp);
            });

            // add connections

            _.each(program.components, function(comp, id) {
                var destRect = nameToRect[comp.name];
                console.log('dest', comp.name, destRect, nameToRect);
                if (comp.source) {
                    var srcRect = nameToRect[comp.source];
                    addVisualConnection(srcRect, destRect, CT_NORMAL);
                } else if (comp.source_list) {
                    _.each(comp.source_list, function(source) {
                        var srcRect = nameToRect[source];
                        addVisualConnection(srcRect, destRect, CT_NORMAL);
                    });
                } else if (comp.true_source || comp.false_source) {
                    if (comp.true_source) {
                        var srcRect = nameToRect[comp.true_source];
                        addVisualConnection(srcRect, destRect, CT_NORMAL);
                    }
                    if (comp.false_source) {
                        var srcRect = nameToRect[comp.false_source];
                        addVisualConnection(srcRect, destRect, CT_SHIFTED);
                    }
                }
            });
            // select main
            if (program.main&& program.main in nameToRect) {
                curSelected = nameToRect[program.main];
                selectRect(curSelected, true);
            }
            $("#program-name").text(program.name);
            $("#program-name").editable('setValue', program.name);

        },

        newProgram: function() {
            var name = 'untitled';
            initNewProgram(new Program(inventory, name));
        }
    }
}

