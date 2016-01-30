function api_query(cid, endpoint, args) {
    if (!(endpoint == 'gains' || endpoint == 'histogram' || endpoint == 'comparables' || endpoint == 'lifecycle' || endpoint == 'values')) { return {} }

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

function makeGains( id, cid, selector, breakout) {
    api_query(cid, 'gains', {selector: selector, breakout: breakout}).done(function(data){
        addBreakout(id, breakout_map(data));
    });
};

function makePopulation( id, cid, selector) {
    console.log(selector);
    api_query(cid, 'histogram', {selector: selector, comparable: true}).done(function(data){
        var hist = hist_map(data.histograms)
        addHist(id, hist);
    });
};

function makeBreakout( id, cid, selector, breakout) {
    console.log(id);
    api_query(cid, 'comparables', {selector:selector, breakout:breakout}).done( function(data) {
        addBreakout(id, breakout_map(data));
    });
}

function breakout_map(api_breakout) {
    plottable = []
    temp = {key: api_breakout.key, values: api_breakout.values.sort(function(a, b) { return a.label.localeCompare(b.label)})}
    console.log("HELLO");
    console.log(api_breakout);
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
        {id:0, text:"Network", value:"network"},
        {id:1, text:"Geo", value:"geo"}, 
        {id:2, text:"Domain", value:"url_domain"},
        {id:3, text: "Content", value:"content_type"},
        {id:4, text: "Size", value:"size"}
    ]
    var logic = [
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
        breakout: baseModels.segment + baseModels.expand,
        filter: baseModels.segment + baseModels.logic + baseModels.values + baseModels.deleteRow,
        newRow: baseModels.newRow
    };

    var makeControls = function() {
            div = $(container).empty()
            if (rows.length == 1 && rows[0].type == 'newRow') {
                //take care of a weird state a user could get to by clicking buttons
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
                    element.on("select2:select", x)
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
                    rows[rowNum].segment = e.params.data.id
                    loadValues(rowNum) //implicitly will call makeControls()
                    //makeControls();
                }
            },
            logic: function(rowNum) {
                return function(e) {
                    rows[rowNum].logic = e.params.data.id
                    makeControls();
                }
            },
            value: function(rowNum) {
                return function(e) {
                    //console.log('setting selected value', $("#segControl-" +rowNum + " .value").val())
                    input = $("#segControl-" + rowNum + " .value").val()
                    console.log('input', input)

                    if (Array.isArray(input)) { //this happens for `in` selections
                        rows[rowNum].selectedVal = input

                    } else { //check whether the input is already in the list of values
                        listItem = $.grep(rows[rowNum].values, function(item) { return item.text == input || item.id == input} )
                        inList = listItem.length > 0 ? listItem[0].id : false

                        if (!inList) { // if the input isn't in the list, add it to the end
                            finalId = rows[rowNum].values.length
                            rows[rowNum].values.push({id: finalId, text: input});
                            inList = finalId
                        }
                    
                        rows[rowNum].selectedVal = inList
                    }
                }
            }
        };

    var loadValues = function(rowNum) {
        //set a flag to disable interaction until values are loaded
        rows[rowNum].wait = true;
        delete rows[rowNum].selectedVal;
        makeControls();

        //grab values to fill drop down, sort by weight of records
        //store them in the `rows` control state variable as a cache
        rowSegment = segments[rows[rowNum].segment].value
        api_query( customer, 'values', {segment: rowSegment}).done( function(data) {
            vals = Object.keys(data.values).map(function (key) {return {text: key, weight: data.values[key] / data.total}})
            vals.sort(function(a,b) {return b.weight - a.weight})
            for (i=0; i<vals.length; i++) { 
                vals[i].id = i+1 
            }
            vals.unshift({id:0, text:''})
            rows[rowNum].values = vals
            
            rows[rowNum].wait = false;
            makeControls();
        })
    }

    var handleSelects = function(element, rowNum) {
        if (element.attr('class') == 'segment') {
            element.select2({
                data: segments,
                disabled: rows[rowNum].wait
            });
            if (rows[rowNum].segment) {
                element.val(rows[rowNum].segment).trigger("change")
            }
        } else if (element.attr('class') == 'logic') {
            element.select2({
                data: logic,
                disabled: rows[rowNum].wait
            });
            if (rows[rowNum].logic) {
                element.val(rows[rowNum].logic).trigger("change")
            }
        } else if (element.attr('class') == 'value') {

            // handle the case where a user can select into an array
            if (rows[rowNum].logic == 4 || rows[rowNum].logic == 5) {
                //console.log('in IN case')
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
        breakout = new String;

        $.map(rows, function(row) {
            if (row.type == 'filter') {
                if (typeof(row.selectedVal) == "string") {
                    valuePhrase = row.values[row.selectedVal].text
                } else if (Array.isArray(row.selectedVal)) {
                    valuePhrase = "(" + $.map(row.selectedVal, function (index) { return row.values[index].text } ).toString() + ")"
                } else {
                    console.log(row.selectedVal)
                    debugger;
                }
                phrase = [segments[row.segment].value, logic[row.logic].value, valuePhrase].join(" ");
                selectors.push(phrase)        
            } else if (row.type == 'breakout') {
                breakout = segments[row.segment].value
            } else {}
        })
        
        return {
            'selector': selectors.join(" and "),
            'breakout': breakout,
            'cid': customer
        }

    };

    var externalControls = function(selectors, breakout) {
        selectorPhrases = '';
    } 

    makeControls(); 
    
    return {
        read: readControls
    }
}


