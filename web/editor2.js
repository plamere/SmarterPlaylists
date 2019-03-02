var createEditor = function(canvasElem, inventory, types, isReadOnly) {
    var program = new Program(inventory, 'my program');
    let graph = null;
    let paper = null;
    let elem = '#' + canvasElem;
    let parent = "#inner-workspace-parent"; // hack
    let fixedHeight = 700;
    var curScale = 1.0;

    var sources = [];
    var filters = [];
    var combiners = [];
    var selectors = [];
    var orders = [];
    var conditionals = [];
    var miscs = [];

    var curSelected = null;
    var altSelected = null;


    var readOnly = isReadOnly === true;
    var widgetCount = 0;
    var xMargin = 40;
    var yMargin = 80;
    var rectWidth = 100;
    var rectHeight = 60
    var fontSize = 14;

    var nameToRect = {};


    console.log("creatEditor");

    function edit(rect) {
        //canvasFocus(false);
        var component = rect.component;

        $("#edit-modal .modal-title").text(component.trans.cls.display);
        $("#edit-modal .description").text(component.trans.cls.description);
        if (component.trans.cls.help) {
            $("#edit-modal .help").html(component.trans.cls.help);
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
            var sel = null;
            function addDescription() {
                if (sel) {
                  console.log('selected', sel.val());
                  var rinfo = getRangeInfo(sel.val());
                  console.log('rinfo', rinfo);
                  if (rinfo && rinfo.description) {
                    var text = rinfo.description;
                    if (rinfo.min_value !== undefined && rinfo.max_value !== undefined) {
                        text += " Valid range: " + rinfo.min_value + " to "
                          + rinfo.max_value;
                    } else if (rinfo.min_value !== undefined) {
                        text += " Valid range: " + rinfo.min_value + " and up"
                    } else if (rinfo.max_value !== undefined) {
                        text += " Valid range: Up to" + rinfo.max_value
                    }
                    description.html(text);
                  } else {
                    description.empty();
                  }
                }
            }

            var div = $("<div class='form-group'>");
            if (false && 'default' in param) {
                curParams[name] = param['default'];
            }

            var opt = param.optional ? "" : " (required) ";
            var dname = 'display' in param ? param['display'] : name;
            if (param.type in types) {
                var label =  $('<label for="' + name + '">').text(dname + opt);
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

                var description = $("<div class='param-description'>");

                sel.on('change', function() {
                    addDescription();
                    curParams[name] = convertType(param.stype, sel.val());
                });
                div.append(label);
                div.append(sel);
                div.append(description)
                addDescription();
            }
            else if (param.type  == 'string' || param.type == 'uri') {

                var label =  $('<label for="' + name + '">').text(dname + opt);
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
            else if (param.type  == 'uri_list') {
                var label =  $('<label for="' + name + '">').text(dname + opt);
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
                var label =  $('<label for="' + name + '">').text(dname + opt);
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
                var label =  $('<label for="' + name + '">').text(dname + opt);
                label.addClass("edit-param-label");
                label.attr('title', param.description);
                var val = component.params[name] != null ?
                          component.params[name] : param['default'];
                var inp = $("<input class='form-control'>").val(val);
                inp.attr('id', name);

                inp.on('change', function() {
                    var val = inp.val();

                    if (val.indexOf('.') >= 0) {
                        curParams[name] = parseFloat(inp.val());
                    } else {
                        curParams[name] = parseInt(inp.val());
                    }
                });
                div.append(label);
                div.append(inp);
            }
            else if (param.type  == 'time') {
                var label =  $('<label for="' + name + '">').text(dname + opt);
                label.addClass("edit-param-label");
                label.attr('title', param.description);
                var val = secsToTimeString(component.params[name] ?
                          component.params[name] : param['default']);
                var inp = $("<input class='form-control'>").val(val);
                inp.attr('id', name);

                inp.on('change', function() {
                    var val = inp.val();
                    curParams[name] = timeStringToSecs(val);
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
                });
                label.text(dname);
                label.attr('title', param.description);
                div.append(label);
                div.append(inp);
            } else if (param.type == 'optional_date') {
                  var val = component.params[name];
                  var ndiv = $("<div>");
                  ndiv.append(
                    $("<label>").text(dname).attr('title', param.description));
                  var datePicker = $("<span>");
                  datePicker.addClass("ncol-sm-4 input-group date");
                  var inp = $("<input>")
                    .attr("type", 'text')
                    .addClass('form-control');

                  inp.on('change', function() {
                      var state = $(inp).is(':checked');
                      var val = inp.val();
                      console.log('input changed, val is', val);
                  });


                  datePicker.append(inp);


                  var btn = $("<span>")
                    .addClass("input-group-addon")
                    .append($("<span>").addClass("glyphicon glyphicon-calendar"))

                  datePicker.append(btn);
                  ndiv.append(datePicker);
                  div.append(ndiv);

                  datePicker.datetimepicker({
                      "useCurrent" :true,
                      "format": 'lll',
                      sideBySide: false,
                  });
                  console.log('val', val);
                  var dateData = datePicker.data('DateTimePicker');
                  datePicker.on("dp.change", function(e) {
                      console.log("dp.change", e);
                      if (e.date == false) {
                        curParams[name] = -1;
                      } else {
                        curParams[name] = e.date.unix();

                      }
                      console.log("date changed", e);
                  });
                  var date = "";
                  if (val == -1) {
                      date = null;
                  } else {
                    date = new Date(0); // The 0 there is the key, which sets the date to the epoch
                    date.setUTCSeconds(val);
                  }
                  dateData.date(date);
            } else {
              console.log("Unknown param type", param.type)
            }
            if (div.children().length > 0) {
                pdiv.append(div);
            }
        }


        var pdiv = $("#edit-modal .params");
        pdiv.empty();

        _.each(component.trans.cls.params, function(param, name) {
            addParam(pdiv, name, param);
        });

        if (pdiv.children().length == 0) {
            $("#parameters").hide();
        } else {
            $("#parameters").show();
        }

        $('#edit-modal').modal({})


        $("#edit-modal").off('hidden.bs.modal');
        $('#edit-modal').on('hidden.bs.modal', function () {
            //canvasFocus(true);
        });

        $("#edit-modal .save").off('click');
        $("#edit-modal .save").on('click', function() {
            _.each(curParams, function(val, name) {
                component.params[name] = val;
            });
            renameComponent(rect);
            program.trans.needsSave = true;
        });
    }

    function initNewProgram(newProgram) {
        console.log("initNewProgram", newProgram);
        widgetCount = 0;
        connections = [];
        nameToRect = {};
        program = newProgram;
        previousComponent = null;
        setInfo(false, '');
    }

    function setInfo(state, verb) {
        if (state) {
            var text = verb || 'running';
            $("#running-state").addClass('text-info');
            $("#running-state").text(text);
        } else {
            $("#running-state").text('');
        }
    }

    function setRunning(state, verb) {
        if (state) {
            var text = verb || 'running';
            $("#running-state").text(text);
            $("#run-button").prop("disabled", true);
            $("#run-button").addClass("icon-red");

        } else {
            $("#running-state").text('');
            $("#run-button").prop("disabled", false);
            $("#run-button").removeClass("icon-red");
        }
    }

    function setInfo(state, verb) {
        if (state) {
            var text = verb || 'running';
            $("#running-state").addClass('text-info');
            $("#running-state").text(text);
        } else {
            $("#running-state").text('');
        }
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

    function initPaper() {
        graph = new joint.dia.Graph;
        console.log("width/height", $(elem).width(), $(elem).height());
         paper = new joint.dia.Paper({
            el: $(elem),
            // TODO make responsive
            width: $(parent).width(),
            height: $(parent).height(),
            model: graph,
            gridSize: 10,
            drawGrid:true,
            background: {
                 color: 'rgba(0, 255, 0, 0.3)'
            }
        });

        $("#zoom-in").click(function() {
            curScale *= 1.3;
            paper.scale(curScale, curScale);
            console.log('zoom-in', curScale);
        });
        $("#zoom-reset").click(function() {
            curScale = 1.0;
            paper.scale(curScale, curScale);
            console.log('zoom-reset', curScale);
        });
        $("#zoom-out").click(function() {
            curScale /= 1.3;
            paper.scale(curScale, curScale);
            console.log('zoom-out', curScale);
        });


        $(window).resize(function() {
            var canvas = $(parent);
            console.log("resizing window", canvas.width(), canvas.height());
            paper.setDimensions(canvas.width(), canvas.height());
        });

        $(parent).bind('keydown', function(event) {
            console.log('keydown', event);
        });

        graph.on('graph-all', function(eventName, cell) {
            console.log(arguments);
        });

        paper.on('paper-all', function(eventName, cell) {
            console.log(arguments);
        });

        quickCheck();

    }

    function addControls() {
        var runButton = $("#run-button");
        runButton.on('click', function() {
            var title = $("#program-name").text();
            var saveToSpotify = $('#save-playlist').is(':checked');
            if (program.name != title) {
                program.name = title;
            }

            var description = $("#program-description").text();
            if (program.description != description) {
                program.description = description;
            }

            clearComponentErrors();
            if (curSelected) {
                var main = curSelected.name;
                var issues = program.check(main);
                program.main = main;
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
                    program.run(main, saveToSpotify, function(data) {
                        setRunning(false);
                        if (data) {
                            if (data.status == 'ok') {
                                showPlaylist(program.name, data);
                            } else {
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
            program.description = $("#program-description").text();
            program.save(function(data) {
                if (data.status == 'ok') {
                    setInfo(true, 'Saved');
                } else {
                    error("Can' save");
                }
            });
        });

        var clearButton = $("#clear-button");
        clearButton.on('click', function() {
            if (window.confirm('Clear all components from this program?')) {
                deleteAll();
            }
        });

        var deleteButton = $("#delete-component-button");
        deleteButton.on('click', function() {
            deleteCur();
        });

        $("#share-button").on('click', function() {
            if (program) {
                program.publish(function(results) {
                    if (results.status == 'ok') {
                        setInfo(true, 'Published');
                    } else {
                        setInfo(true, 'Not Publshed');
                    }
                });
            }
        });
    }

    function setURL(pid) {
        if (pid) {
            var p = '?pid=' + results['pid'];
            history.replaceState({}, '', p);
        } else {
            history.replaceState({}, '', '');
        }
    }

    function initUI() {
        if (!readOnly) {
            addControls();
            showInventoryUI();
        }
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

    function moveTo(rect, x, y) {
        // TODO update extra on drag
        rect.position(x,y);
        rect.component.extra.x = x;
        rect.component.extra.y = y;
        program.trans.needsSave = true;
    }

    function findTypeName(key, type) {
        var name = '?';
        _.each(type, function(t) {
            if (key == t.value) {
                name =  t.name;
            }
        });
        return name;
    }

    function addNewComponent(componentType, comp) {
        var col = widgetCount * 12;
        var row = widgetCount * 12;
        var xpos = xMargin + col;
        var ypos = yMargin + row;
        var fontSize = 12;
        var rect = null;

        console.log("addNewComponent", componentType, comp);
        if (componentType.name == "comment") {
            rect = paper.rect(xpos, ypos, commentWidth, tileHeight, 4);
            rect.textXOffset = commentWidth / 2;
            rect.textYOffset = 30;
            rect.color = "#eeeeee";
            rect.selectable = false;
            rect.attr({
                fill: "#eeeeee",
                stroke: rect.color,
                opacity: .4,
                "stroke-width": 0,
                cursor: "move",
                });
            fontSize = 18;
        } else {
            rect = createRect(componentType.name);
            // add the ports
        }


        //addLabel(rect, componentType.name);

        rect.inEdges = {};
        rect.outEdges = {};

        if (comp) {
            rect.component = comp;
            rect.name = comp.name;
            moveTo(rect, comp.extra.x, comp.extra.y);
        } else {
            rect.name = nextComponentName(componentType);
            console.log("prog", program);
            rect.component = program.addComponent(rect.name, componentType.name, {}, {});
            _.each(rect.component.trans.cls.params, function(param, name) {
                if ('default' in param) {
                    rect.component.params[name] = param['default'];
                } else if (param.type == 'bool') {
                    rect.component.params[name] = false;
                }
            });
            moveTo(rect, xpos, ypos);
        }
        renameComponent(rect);
        rect.addTo(graph);

        console.log("CR RECT", rect);
        _.each(rect.component.trans.cls.params, function(param, name) {
            if (param.type == "port") {
                var port = {
                    group: param.port,
                    label: name
                };
                console.log("addPort", port);
                rect.addPort(port);
            }
        });


        // Set component param defaults and rename
        // component
        nameToRect[rect.name] = rect;
        return rect;
    }

    function makeSubs(title, component) {
        var out = []

        function makeSub(word, component) {
            var key  = word.replace('$', '');
            var showNegBool = false;
            var flexiState = false;
            var trueVal = '';
            var falseVal = '';
            if (key.indexOf('?') == 0) {
                //?val:true-text:false-text
                var vals = key.split(':')
                if (vals.length == 3) {
                    trueVal = vals[1].replace('-', ' ')
                    falseVal = vals[2].replace('-', ' ')
                    key  = vals[0].replace('?', '')
                    flexiState = true;
                    console.log('flexi', key, trueVal, falseVal);
                }
            }
            else if (key.indexOf('!!') == 0) {
                showNegBool = true;
                key  = key.replace('!!', '');
            }
            if (key in component.params) {
                var keyType = component.trans.cls.params[key].type;
                if (keyType in types) {
                    key = findTypeName(component.params[key], types[keyType]);
                    return key;
                } else if (keyType == 'bool') {
                    if (flexiState) {
                        if (component.params[key]) {
                            return trueVal;
                        } else {
                            return falseVal;
                        }
                    }
                    else if (component.params[key]) {
                        return key;
                    } else {
                        return showNegBool ? "not " + key : "";
                    }
                } else if (keyType == 'time') {
                    return fmtTime(component.params[key]);
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

    function renameComponent(rect) {
        var title = rect.component.trans.cls.title || rect.component.trans.cls.display;
        title = makeSubs(title, rect.component);
        addLabel(rect, title);
        // rect.label.attr('text', title + '\n' + 'more lines');
    }

    function addLabel(rect, text) {
        console.log('addLabel', text, rect);
        var wrappedText = joint.util.breakText(text, { width: rectWidth, height: rectHeight, 'font-size':fontSize });
        rect.attr('label/text', wrappedText);
    }
    
    function initEditor() {
        initPaper()
        sortComponents();
        assignColorsToInventory();
        initUI();
        var elemName = "#" + canvasElem;
        if (!readOnly) {
            //$(document).keydown(keydown);
            //$(document).keyup(keyup);
        }

        // if the callback.html was able to successfully save
        // we get this event, so update the program and save it
        // with the uri that was created for the playlist
        /* TBD OLD, REMOVE
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
        */

        // TODO:  Instead of always saving programs, we might add
        //  and onbeforeunload event that will save just the dirty ones
        //  before we exit.
        if (!isReadOnly) {
            $('#program-name').editable({
                type: 'text',
                title: 'Enter Program Name',
                placement: 'bottom',
                showbuttons: 'bottom',
                inputclass: 'nprogram-input',
                tpl: "<input type='text' style='width: 600px'>",
                success: function(response, newValue) {
                    program.name = newValue;
                    program.trans.needsSave = true;
                 }
            });
            $('#program-description').editable({
                type: 'text',
                title: 'Enter Program Description',
                placement: 'bottom',
                showbuttons: 'bottom',
                inputclass: 'description-input',
                tpl: "<input type='text' style='width: 600px'>",
                success: function(response, newValue) {
                    program.description = newValue;
                    program.trans.needsSave = true;
                 }
            });
        }
    }

    function getNextColor() {
        return "#121212";
    }

    function assignColorsToInventory() {
        _.each(inventory, function(component, name) {
            component.color = getNextColor();
        });
    }

    function addComponentType(elem, comp) {
        var button = $("<li>")
            .text(comp.display)
            .attr('title', comp.description);
        elem.append(button);
        button.on('click', function() {
            var newComponent = addNewComponent(comp);
            /* TODO
            if (previousComponent && !isConnected(previousComponent)) {
                connectComponent(previousComponent, newComponent, "green");
            }
            */
            previousComponent = newComponent;
            // select.apply(newComponent);
        });
    }

    function isConnected(comp) {
    }

    function showInventoryItem(members, elem) {
        members.sort(function(a,b) {
            return a.display.localeCompare(b.display);
        });

        var node = $(elem);
        _.each(members, function(member) {
            addComponentType(node, member);
        });
    }

    function showInventoryUI() {

        showInventoryItem(sources, "#sources");
        showInventoryItem(combiners, "#combiners");
        showInventoryItem(selectors, "#selectors");
        showInventoryItem(filters, "#filters");
        showInventoryItem(orders, "#orders");
        showInventoryItem(conditionals, "#conditionals");
        showInventoryItem(miscs, "#miscs");
    }

    function sortComponents() {
        _.each(inventory, function(component, name) {
            if (component.type == 'filter') {
                filters.push(component);
            } else if (component.type == 'combiner') {
                combiners.push(component);
            } else if (component.type == 'selector') {
                selectors.push(component);
            } else if (component.type == 'order') {
                orders.push(component);
            } else if (component.type == 'conditional') {
                conditionals.push(component);
            } else if (component.type == 'misc') {
                miscs.push(component);
            } else if (component.type == 'source') {
                sources.push(component);
            }
            else {
                alert('unsupported ' + component.type);
            }
        });
    }

    function selectRect(rect, selected) {
        rect.attr({
            body: {
                fill: selected ? "#DD4444" : '#2C3E50',
                rx:5, ry:5, 
                strokeWidth: selected ? 6 : 2
            },
        });
    }

    function createRect(text, xpos, ypos) {
        console.log("createRect", text, xpos, ypos);
        var rect = new joint.shapes.standard.Rectangle();
        rect.position(xpos, ypos);
        rect.resize(rectWidth, rectHeight);
        rect.attr({
            body: {
                fill: '#2C3E50',
                rx:5, ry:5, 
                strokeWidth:2
            },
            label: {
                text: text,
                fill: 'white',
                fontSize:fontSize,
            }
        });
        return rect;
    }

    function quickCheck() {
        var rect = new joint.shapes.standard.Rectangle();
        rect.position(100, 30);
        rect.resize(100, 40);
        rect.attr({
            body: {
                fill: '#2C3E50',
                rx:5, ry:5, 
                strokeWidth:2
            },
            label: {
                text: 'Hello',
                fill: 'white',
                fontSize:18,
            }
        });

        rect.addTo(graph);
        var rect2 = rect.clone();
        rect2.translate(300, 0);
        rect2.attr('label/text', 'world');
        rect2.addTo(graph);

        rect2.translate(300, 0);
        rect2.attr('label/text', 'world');
        rect2.addTo(graph);

        var rect3 = rect.clone();
        rect3.translate(200, 50);
        rect3.attr('label/text', 'world');
        rect3.addTo(graph);


        var router = "manhattan";
        var link = new joint.shapes.standard.Link();
        link.source(rect);
        link.target(rect2);
        link.addTo(graph);
        link.router(router);

        var removeTool = new joint.linkTools.Remove();
        var toolsView = new joint.dia.ToolsView({
            tools: [removeTool]
        });
        var linkView = link.findView(paper);
        linkView.addTools(toolsView);
        linkView.hideTools();

        var link = new joint.shapes.standard.Link();
        link.source(rect3);
        link.target(rect2);
        link.addTo(graph);
        link.router(router);
        var removeTool = new joint.linkTools.Remove();
        var toolsView = new joint.dia.ToolsView({
            tools: [removeTool]
        });
        var linkView = link.findView(paper);
        linkView.addTools(toolsView);
        linkView.hideTools();

        graph.on('all', function(eventName, cell) {
            // console.log(arguments);
        });



        paper.on('link:mouseenter', function(linkView) {
            linkView.showTools();
        });

        paper.on('link:mouseleave', function(linkView) {
            linkView.hideTools();
        });

        paper.on('element:pointerdblclick', function(elementView) {
            var currentElement = elementView.model;
                currentElement.attr('body/stroke', 'orange')
            console.log("dblclick currentElement", currentElement);
            edit(currentElement);
        });

        paper.on('cell:pointerdown', function(elementView) {
            var currentElement = elementView.model;
            console.log("single click", currentElement);
            if (curSelected) {
                selectRect(curSelected, false);
            }
            curSelected = currentElement;
            // curSelected.attr('body/stroke', 'green');
            selectRect(curSelected, true);
        });
               
    }

    initEditor();
    return {
        load:function(newProgram) {
            console.log("loadPrgram!!!");
            if (newProgram == null) {
                return;
            }
            initNewProgram(newProgram);

            _.each(program.components, function(comp, id) {
                addNewComponent(comp.trans.cls, comp);
            });

            // add connections

          // conn
            _.each(program.components, function(comp, id) {
                var connections = getIncomingConnections(comp);
                _.each(connections, function(carry) {
                    var portName = carry[0];
                    var srcName = carry[1];
                    var destName = carry[2];
                    var portType = carry[3];
                    var srcRect = nameToRect[srcName];
                    var destRect = nameToRect[destName];
                    addVisualConnection(srcRect, destRect, portType);
                });
            });
            // select main
            if (program.main&& program.main in nameToRect) {
                curSelected = nameToRect[program.main];
                selectRect(curSelected, true);
            }
            $("#program-name").text(program.name);
            $("#program-description").text(program.description);
            if (!isReadOnly) {
                $("#program-name").editable('setValue', program.name);
                $("#program-description").editable('setValue', program.description);
            }

            program.trans.needsSave = false;
        },

        newProgram: function() {
            console.log("newPrgram!!!");
            var name = 'untitled';
            initNewProgram(new Program(inventory, name));
        }
    }
}
