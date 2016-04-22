function api_query(cid, endpoint, args) {
    //if (!(endpoint == 'gains' || endpoint == 'histogram' || endpoint == 'comparables' || endpoint == 'lifecycle' || endpoint == 'values')) { return {} }

    api_url = [window.base_api, cid, endpoint].join('/')
    xhr = $.ajax({
        url: api_url,
        type: "get",
        data: args
    })

    return xhr
}

//function getCIDs( id ) {
//    api_query( 'cids' ).done(function(data) {cidDropDown(id, data)});
//}

function makeGains( id, controls) {
    api_query(controls.cid, 'gains', {selector: controls.selector, breakout: controls.breakout}).done(function(data){
        addBreakout(id, breakout_map(data));
    });
};

function makePopulation( id, controls) {
    api_query(controls.cid, 'histogram', {selector: controls.selector, comparable: true}).done(function(data){
        var hist = hist_map(data.histograms)
        addHist(id, hist);
    });
};

function makeBreakout( id, controls) {
    api_query(controls.cid, 'comparables', {selector:controls.selector, breakout:controls.breakout}).done( function(data) {
        addBreakout(id, breakout_map(data));
    });
}

function breakout_map(api_breakout) {
    plottable = []
    temp = {key: api_breakout.key, values: api_breakout.values.sort(function(a, b) { return a.label.localeCompare(b.label)})}
    for ( datapoint in temp.values ) {
        temp.values[datapoint].value *= 100
    };
    plottable.push(temp);
    console.log(plottable)
    return plottable
}

function hist_map(api_hist) {
    plottable = []
    for (entry in api_hist) {
        i = 0;
        vals = api_hist[entry].values.sort(function(a,b){return a.x - b.x});
        new_vals = [];
        total = 0;
        while (i < vals.length && total < .8) {
            temp = {x: vals[i].x, y: 100 * Math.round(10000 * vals[i].y)/10000} //round math for percent of population to two decimal places
            new_vals.push(temp)
            total += vals[i].y
            i += 1;
        }
        plottable.push({key: api_hist[entry].key, values: new_vals})
    }

    console.log(plottable)

    return plottable
}

function gain_map(api_gain) {
    console.log('gain_map');
    var series = [];

    for (subset in api_gain.gains) {
        api_gain.gains[subset].value *= 100;
        console.log( subset + ' has significance of: ' + api_gains[subset] );
    }

    Object.keys(api_gain).map(function(label, i) {
        series.push(api_gain[label])
    });
    return [{key:'gains', values:series}];
}

function addHist(id, data) { 
    id = id + " svg"
    nv.addGraph({
        generate: function() {
            var width = $(id).outerWidth(),
                height = 240; 

            var chart = nv.models.lineChart()
                //.width(width)
                .height(240)
                //.showYAxis(false)
                //.stacked(false)
                //.showControls(false)
                //.isArea(true)
                ;

            chart.dispatch.on('renderEnd', function(){
                console.log('Render 2 Complete');
            });
            d3.select(id)
                .datum(data)
                .attr('width', width)
                .attr('height', height)
                .transition().duration(0)
                .call(chart);

            return chart;
        },
        callback: function(chart) {
            nv.utils.windowResize(function() {
                var width = $(id).outerWidth();
                var height = 240; 
                chart.width(width).height(height);

                d3.select(id)
                    .attr('width', width)
                    .attr('height', height)
                    .transition().duration(0)
                    .call(chart);
            });
        }
    });
}


function addBreakout(id, data) {

    var id = id + " svg";

    nv.addGraph({
        generate: function() {
            var width = $(id).outerWidth(),
                height = 240;

            var chart = nv.models.discreteBarChart()
                .width(width)
                .height(height)
                .x(function(d) { return d.label })    //Specify the data accessors.
                .y(function(d) { return d.value })
                .staggerLabels(true)    //Too many bars and not enough room? Try staggering labels.
                .tooltips(true)
                .tooltipContent(function(key, y, e, graph) { return 'Significance: '+ 100*Math.round(10000*key.data.significance)/10000 })
                .showValues(true)       //...instead, show the bar value right on top of each bar.
                ;
           

            d3.select(id)
                .datum(data)
                .attr('height', height)
                .transition().duration(0)
                .call(chart);

            return chart;
        },
        callback: function(graph) {
            nv.utils.windowResize(function() {
                var width = $(id).outerWidth();
                var height = 240;
                graph.width(width).height(height);

                d3.select(id)
                    .attr('width', width)
                    .attr('height', height)
                    .transition().duration(0)
                    .call(graph);
            });
        }
    });
}

//UI Selectboxes

var segControls = function(id, cid) {

    var container = id
    var customer = cid
    var segments = [
        "",
        {id:1, text:"Network", value:"network"},
        {id:2, text:"Geo", value:"geo"}, 
        {id:3, text:"Domain", value:"url_domain"},
        {id:4, text:"Content", value:"content_type"},
        {id:5, text:"Size", value:"size"},
        {id:6, text:"Schema", value:"schema"},
        {id:7, text:"SDK Version", value:"sdk_version"}
    ]
    var logics = [
        {id:0, text:"Equals", value: "="},
        {id:1, text:"Not Equal", value: "not ="},
        {id:2, text:"Like", value: "like"},
        {id:3, text:"Not Like", value: "not like"},
        {id:4, text:"In", value:"in"},
        {id:5, text:"Not In", value:"not in"}
    ]

    var rows = [{type: 'breakout', segment: 0}] //initial state
    
    baseModels = {
        segment: "<select class='segment' style='width:20%'></select>",
        logic: "<select class='logic' style='width: 15%'></select>",
        values: "<select class='value' style='width: 50%'></select>",
        expand: "<button class='expand'>></button>",
        newRow: "<button class='newRow'>+</button>",
        deleteRow: "<button class='deleteRow'>X</button>",
    };

    models = {
        breakout: baseModels.segment,
        breakoutPlus : baseModels.segment + baseModels.expand,
        filter: baseModels.segment + baseModels.logic + baseModels.values + baseModels.deleteRow,
        newRow: baseModels.newRow
    };

    var makeControls = function() {
            div = $(container).empty()
            if (rows.length == 1 && rows[0].type == 'newRow') {
                //take care of a weird state a user could get to by clicking deleteRow buttons
                rows[0].type = 'breakout'
            };
            $.map(rows, function(item, index) {
                if (item.type in models) {
                    row = $("<div/>")
                            .append(models[item.type])
                            .attr('class', item.type)
                }
                row.attr('id', "segControl-" + index);
                div.append(row);
            });
            $.map($(container).children(), function(row, rowNum) { makeUseful(rowNum); });
        }

    var addListener = function(element, rowNum) {
        //loop through the html rows and add listeners
        cls = element.attr('class')
        $.each(listeners, function(targetClass, listener) {
            //console.log('key', targetClass, 'value', listener, 'fix later')
            if (cls.indexOf(targetClass) > -1) {
                x = listener(rowNum)
                if (element.is('select')){
                    element.on("change", x)
                } else {
                    element.click(x);
                }
            }
        });
    }

    var listeners = {
            expand: function(rowNum) {
                return function() {
                    rows[rowNum].type = 'filter';
                    rows[rowNum].logic = 0;
                    rows.push({type: 'newRow'});
                    loadValues(rowNum);
                    makeControls();
                }
            },
            newRow: function(rowNum) {
                //turn a + button into a breakout
                return function() {
                    rows[rowNum].type = 'breakout';
                    rows[rowNum].segment = 0;
                    makeControls();
                }
            },
            deleteRow: function(rowNum) {
                //remove this row from the controls
                return function() {
                    rows.splice(rowNum, 1)
                    makeControls();
                };
            },
            segment: function(rowNum) {
                //register the selection
                return function(e) {
                    console.log('segment change event', e)
                    segment = $("#segControl-" + rowNum + " .segment").val()
                    console.log('chosen segment', segment)
                    rows[rowNum].segment = segment
                    if (rows[rowNum].type == "breakout") {
                        rows[rowNum].type = "breakoutPlus"
                    }
                    loadValues(rowNum, function() { makeControls() });
                }
            },
            logic: function(rowNum) {
                return function(e) {
                    logic = $("#segControl-" + rowNum + " .logic").val()
                    rows[rowNum].logic = logic
                    console.log('chosen logic?', logic)
                    makeControls();
                }
            },
            value: function(rowNum) {
                return function(e) {
                    input = $("#segControl-" + rowNum + " .value").val()
                    selectValue(rowNum, input)
                }
            }
        };

    var selectValue = function(rowNum, val) {

        var matcher = function (rowNum, val) {
                        listItem = $.grep(rows[rowNum].values, function(item) {
                            return item.text == val || item.id == val
                        })
                        return listItem[0] || false
                    }

        if (Array.isArray(val)) { //this happens for `in` selections
            matchedItems = val.map(function(item) { return matcher(rowNum, item) })
            select = matchedItems.map( function(item) {return item.id})

        } else { //check whether the input is already in the list of values
            listItem = matcher(rowNum, val)
            inList = listItem ? listItem : false

            if (inList) {
                console.log('input was found in the list', val, inList)
                select = inList.id
            } else if (!inList) { // if the input isn't in the list, add it to the end
                                  // this happens for some `like` selections
                finalId = rows[rowNum].values.length
                newItem = {id: finalId, text:val}
                rows[rowNum].values.push(newItem);
                select = newItem.id
            }

         
        }
        console.log("setting value at id", typeof(select), select)
        rows[rowNum].selectedVal = select
    }

    var loadValues = function(rowNum, callback) {
        //return a Promise
        return new Promise(function(resolve) {
            //set a flag to disable interaction until values are loaded
            rows[rowNum].wait = true;
            delete rows[rowNum].selectedVal;
            makeControls();

            var whenDone = $.isFunction(callback) ? callback : new Function 

            //grab values to fill drop down, sort by weight of records
            //store them in the `rows` control state variable as a cache
            rowSegment = segments[rows[rowNum].segment].value
            
            api_query( customer, 'values', {segment: rowSegment}).done( function(data) {

                rows[rowNum].values = formatOptions(data)
                
                rows[rowNum].wait = false;
                makeControls();
                
                //execute the callback
                //whenDone()
                resolve(whenDone());
            })
        })
    }

    var formatOptions = function(data) {
        vals = Object.keys(data.values).map( function (key) {
                    return { text: key, weight: data.values[key] / data.total }
                })
        
        vals.sort( function (a,b) { return b.weight - a.weight })

        //shift stuff to allow for a placeholder
        for (i=0; i<vals.length; i++) {
            vals[i].id = i+1
        }
        vals.unshift("")
        
        return vals
    }

    var handleSelects = function(element, rowNum) {
        if (element.attr('class') == 'segment') {
            element.select2({
                data: segments,
                placeholder: "Segments",
                disabled: rows[rowNum].wait
            });
            if (rows[rowNum].segment) {
                element.val(rows[rowNum].segment).trigger("change")
            }
        } else if (element.attr('class') == 'logic') {
            element.select2({
                data: logics,
                disabled: rows[rowNum].wait
            });
            if (rows[rowNum].logic) {
                element.val(rows[rowNum].logic).trigger("change")
            }
        } else if (element.attr('class') == 'value') {

            // handle the case where a user can select into an array
            if (rows[rowNum].logic == 4 || rows[rowNum].logic == 5) {
                element.attr('multiple', 'multiple')
            }

            element.select2({
                data: rows[rowNum].values || [],
                disabled: rows[rowNum].wait,
                multiple: (rows[rowNum].logic == 4 || rows[rowNum].logic == 5) ? true : false, //support multiple selections for `in` queries
                tags: (rows[rowNum].logic == 2 || rows[rowNum].logic == 3) ? true : false //support custom entries for `like` queries
            })

            //populate selections if already made
            if (rows[rowNum].selectedVal) {
                console.log('handling value select', rows[rowNum].selectedVal)
                element.val(rows[rowNum].selectedVal).trigger("change")
            }
        }
    }
 

    var makeUseful = function(rowNum) {
        $.map($("#segControl-" + rowNum).children(), function(element, indexInRow) {
            element = $(element)
            if (element.is('select')) {
                handleSelects(element, rowNum);
            } 
            addListener(element, rowNum);
        })
    };

    var readControls = function() {
        selectors = new Array;
        breakout = new String();

        $.map(rows, function(row) {
            if (row.type == 'filter') {
                if (typeof(row.selectedVal) == "number") {
                    valuePhrase = row.values[row.selectedVal].text
                } else if (Array.isArray(row.selectedVal)) {
                    console.log('the selectedVal is an array', row)
                    valuePhrase = "(" +
                        $.map(row.selectedVal, function (index) { return row.values[index].text } ).toString() + 
                        ")"
                } else {
                    console.log('u wot m8?', row, row.selectedVal)
                }
                phrase = [segments[row.segment].value, logics[row.logic].value, valuePhrase].join(" ");
                selectors.push(phrase)        
            } else if (row.type.indexOf("breakout") > -1) {
                //this handles an unset 'breakout' or a set 'breakoutPlus'
                //the ternary is required because select2 needs a blank object at the 0 position
                //which means a .value attribute won't be set for breakout argument
                //on page loads with only a cid specified
                breakout = row.segment != 0 ? segments[row.segment].value : ""
            } else {}
        })
        
        return {
            'selector': selectors.join(" and "),
            'breakout': breakout,
            'cid': customer
        }

    };

    var externalControls = function(selectors, breakoutSegment, callback) {

        if (selectors || breakoutSegment) {
            //things are being set externally, remove stub rows variable
            rows = []
        }

        var cB = $.isFunction(callback) ? callback : new Function
        
        selectorPhrases = selectors ? selectors.split(" and ") : false
        breakout = breakoutSegment ? breakoutSegment : false
        
        var translator = function (item) {
            item = item.split(" ");
            segment = item.shift()
            value = item.pop()



            //entries in item are logic but 'not'-ed logic requires special case
            not = $.inArray('not', item) > -1;
            if (not) {
                logic = item.join(" ")
            } else {
                logic = item[0]
            }

            return {
                segment: segment,
                logic: logic,
                value: value
            }
        }

        if (selectorPhrases) {

            //set up a callback to set selectVal when the values load
            var callback = function(rowNum, value) {
                                return function() {
                                    selectValue(rowNum, value);
                                    makeControls();
                                }
                            }

            toLoad = selectorPhrases.map( function(phrase, index) {                
                rowInfo = translator(phrase);
                segOption = $.grep(segments, function(segment) { return segment.value == rowInfo.segment })
                logicOption = $.grep(logics, function(comparator) { return comparator.value == rowInfo.logic })
                
                console.log(logicOption)
                if (logicOption[0].value.indexOf('in') > -1) {
                    console.log('We have a list', rowInfo.value)
                    rowInfo.value = rowInfo.value.replace('(','').replace(')','').split(',')
                }
                rows[index] = {type: "filter", segment: segOption[0].id, logic: logicOption[0].id}
                whenDone = callback(index, rowInfo.value)
                return loadValues(index, whenDone)
            })

        } else {
            toLoad = false;
        }

        if (breakout) {
            segOption = $.grep(segments, function(segment) { return segment.value == breakout })
            rows.push({type: "breakoutPlus", segment: segOption[0].id})
            makeControls();
        } else {
            rows.push({type: 'newRow'})
        }

        if (toLoad) {
            //execute callback
            Promise.all(toLoad).then(function() { console.log('toLoad', toLoad); cB() });
        } else {
            cB()
        }

    } 

    makeControls(); 
    
    return {
        read: readControls,
        set: externalControls
    }
}
