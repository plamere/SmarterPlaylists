var createEditor = function(canvasElem, inventory) {
    var tileWidth = 100;
    var tileHeight = 80;
    var textXOffset = tileWidth / 2;
    var textYOffset = 30;
    var xMargin = 40;
    var yMargin = 80;
    var sources = []
    var filters = []
    var tWidth = (tileWidth + xMargin);
    var widgetsPerRow = 0;

    var widgets = [];
    var widgetCount = 0;
    var connections = [];
    var controlled = false;
    var shifted = false;
    var program = createProgram(inventory, 'my program');
    var previousComponent = null;
    var curSelected = null;
    var altSelected = null;
    var paper = null;
    var editing = false;

    function initPaper() {
        var top = 100;
        var w = $(window).width();
        var h = $(window).height() - top;

        console.log('width', w, 'height', h);
        paper = Raphael(canvasElem, w, h);
        widgetsPerRow = Math.floor(paper.canvas.offsetWidth / tWidth);
    }

    var dragger = function () {
        var rect = this;
        if (this.parent) {
            rect = this.parent;
        }

        rect.ox = rect.type == "rect" ? rect.attr("x") : rect.attr("cx");
        rect.oy = rect.type == "rect" ? rect.attr("y") : rect.attr("cy");
        rect.animate({"fill-opacity": .2}, 500);

    }

    function deleteCur() {
        if (curSelected) {
            deleteComponent(curSelected);
            curSelected = null;
        }
    }

    function connectComponents() {
        if (altSelected && curSelected && altSelected != curSelected) {
            connectComponent(altSelected, curSelected);
        }
    }

    function deleteComponent(comp) {
        disconnectComponent(comp);
        program.removeComponent(comp.name);
        comp.label.remove();
        comp.remove();
    }

    function keydown(evt) {

        if (editing) {
            return;
        }
        console.log('key', evt.which);
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
        var att = rect.type == "rect" ? 
            {x: newX, y: newY} : 
            {cx: newX, cy: newY};

        rect.attr(att);
        if (rect.label) {
            var lattr = { x: newX + textXOffset, y: newY + textYOffset }
            rect.label.attr(lattr);
        }

        for (var i = connections.length; i--;) {
            paper.connection(connections[i]);
        }
        console.log('shifted', shifted);
    };

    var up = function () {
        var rect = this;
        if (this.parent) {
            rect = this.parent;
        }
        rect.animate({"fill-opacity": 0}, 500);
    };

    function selectRect(rect, state) {
        if (state) {
            rect.attr({'stroke-width' : 6});
        } else {
            curSelected.attr({'stroke-width' : 1});
        }
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

        console.log('editing', rect.name);
        console.log(rect);
        editing = true;
        var component = rect.component;
        console.log('edit', rect.name, component.cls);

        $("#edit-modal .modal-title").text(component.type);
        $("#edit-modal .description").text(component.cls.description);

        var curParams = {};

        function addParam(pdiv, name, param) {
            var div = $("<div class='form-group'>");
            console.log('add param', name, param);

            if ('default' in param) {
                curParams[name] = param['default'];
            }

            if (param.type  == 'string' || param.type == 'uri') {

                var label =  $('<label for="' + name + '">').text(name);
                label.attr('title', param.description);
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
                var label =  $('<label for="' + name + '">').text(name);
                label.attr('title', param.description);
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
            }
            else if (param.type  == 'number') {
                var label =  $('<label for="' + name + '">').text(name);
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
                    console.log('nmber', name, curParams);
                });
                div.append(label);
                div.append(inp);
            }
            else if (param.type  == 'bool') {
                var label =  $('<label for="' + name + '">').text(name);
                var val = component.params[name];
                var inp = $("<input type='checkbox' class='oform-control'>");
                inp.attr('id', name);
                inp.on('change', function() {
                    var state = $(inp).is(':checked');
                    curParams[name] = state;
                });
                label.append(inp);
                div.append(label);
            }
            pdiv.append(div);
        }

        console.log('b4', component.params);
        
        var pdiv = $("#edit-modal .params");
        pdiv.empty();
        _.each(component.cls.params, function(param, name) {
            if (name != 'source') {
                addParam(pdiv, name, param);
            }
        });

        $('#edit-modal').modal({})


        $('#edit-modal').on('hidden.bs.modal', function () {
            editing = false;
            console.log('done editing');
        });

        $("#edit-modal .save").on('click', function() {
            console.log('saving', curParams);
            _.each(curParams, function(val, name) {
                component.params[name] = val;
            });
            console.log('after', component.params);
            renameComponent(rect);
            console.log('editing', rect.name);
        });

    }

    function renameComponent(rect) {
        console.log('renamec', rect, rect.component);

        var title = rect.component.cls.title || rect.component.cls.name;
        title = makeSubs(title, rect.component);
        addLabel(rect, title);
        // rect.label.attr('text', title + '\n' + 'more lines');
    }

    function makeSubs(title, component) {
        var out = []

        function makeSub(word, component) {
            var key  = word.replace('$', '');
            if (key in component.params) {
                if (component.cls.params[key].type == 'bool') {
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
            console.log('word', word);
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


    function connectComponent(source, dest) {

        if (dest.component.maxInputs == 0) {
            return;
        }

        if (dest.component.maxInputs == 1) {
            disconnectInputs(dest);
        }
        disconnectOutputs(source);

        var edge = paper.connection(source, dest, "#f33");
        connections.push(edge);
        edge.source = source
        edge.dest = dest;
        program.addConnection(source.name, dest.name);
        source.outEdges[dest.name] = edge;
        dest.inEdges[source.name] = edge;
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

    function disconnectOutputs(comp) {
        _.each(comp.outEdges, function(edge, destName) {
            removeEdge(edge);
        });
    }


    function nextComponentName(component) {
        widgetCount++;
        return component.name + '-' + widgetCount
    }


    function addNewComponent(component) {
        var col = widgetCount % widgetsPerRow;
        var row = Math.floor(widgetCount / widgetsPerRow);
        var xpos = xMargin + col * (tileWidth + xMargin);
        var ypos = yMargin + row * (tileHeight + yMargin)

        var name = nextComponentName(component);
        var rect = paper.rect(xpos, ypos, tileWidth, tileHeight, 4);
        var color = Raphael.getColor();

        rect.name = name;
        rect.attr({
            fill: color, 
            stroke: color, 
            "fill-opacity": .5, 
            "stroke-width": 2, 
            cursor: "move",
            });


        rect.label = paper.text(xpos + textXOffset, 
            ypos + textYOffset, component.name);
        rect.label.parent = rect;


        rect.label.attr({
            fill: color, 
            stroke: color, 
            cursor: "move",
            "font-size": 12
        });

        addLabel(rect, component.name);

        rect.inEdges = {};
        rect.outEdges = {};
        rect.drag(move, dragger, up);
        rect.label.drag(move, dragger, up);

        rect.dblclick(edit);
        rect.label.dblclick(edit);

        rect.click(select);
        rect.label.click(select);

        rect.component = program.addComponent(name, component.name, {}, {});

        if (previousComponent) {
            connectComponent(previousComponent, rect);
        }
        previousComponent = rect;
        console.log('adding component', component.name, rect);

        // Set component param defaults and rename
        // component
        _.each(rect.component.cls.params, function(param, name) {
            if ('default' in param) {
                rect.component.params[name] = param['default'];
            } else if (param.type == 'bool') {
                rect.component.params[name] = false;
            }
        });
        renameComponent(rect);
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

    function showInventoryUI() {
        var sourceList = $("#sources");
        sourceList.empty();
        _.each(sources, function(source) {
            var sourceComponent = $("<button class='component-button label label-primary'>").text(source.name);
            sourceList.append(sourceComponent);
            sourceComponent.on('click', function() {
                addNewComponent(source);
            });
        });

        var filterList = $("#filters");
        _.each(filters, function(filter) {
            var filterComponent = $("<button class='component-button label label-info'>").text(filter.name);
            filterList.append(filterComponent);
            filterComponent.on('click', function() {
                addNewComponent(filter);
            });
        });
    }

    function sortComponents() {
        console.log('sort', inventory);
        _.each(inventory, function(component, name) {
            if (component.type == 'filter') {
                filters.push(component);
            }
            else if (component.type == 'multi-in-filter') {
                filters.push(component);
            }
            else if (component.type == 'source') {
                sources.push(component);
            } 
            else {
                alert('unsupportd ' + component.type);
            }
        });
    }

    function addButtons() {
        console.log('addbut');
        var button = $("<button class='btn primary'>").text("run");
        button.on('click', function() {
            if (curSelected) {
                var main = curSelected.name;
                var jsonProgram = program.toJson(main);
                console.log('json program', jsonProgram);
                postProgram(jsonProgram, function(data) {
                    if (data) {
                        showPlaylist(data);
                    }
                });
            } else {
                alert("select a component to run");
            }
        });
        $("#controls").append(button);
    }


    function initUI() {
        addButtons();
        showInventoryUI();
    }

    function initEditor() {
        initPaper()
        sortComponents();
        initUI();
        var elemName = "#" + canvasElem + '-parent';
        $(document).keydown(keydown);
        $(document).keyup(keyup);
    }

    initEditor();
    return {    
    }
}

