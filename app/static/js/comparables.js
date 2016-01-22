function api_query(cid, endpoint, args) {
    if (!(endpoint == 'gains' || endpoint == 'histogram' || endpoint == 'comparables' || endpoint == 'lifecycle')) { return {} }

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
    console.log(temp)
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
        api_gain.gains[subset].value *= 100
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
                .tooltips(false)        //Don't show tooltips
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
var segControls = function(id) {
    var container = id
    var segments = [{id:0, text:"Network"}, {id:1, text:"Geos"}]
    var rows = [{type: 'breakout', segment: segments[0]}]
    var logic = [{id:0, text:"Equals", value: "="}, {id: 1, text:"Not Equal", value: "not ="}]

    baseModels = {
        segment: "<select class='segment' style='width:30%'></select>",
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
            $.map($(container).children(), function(row, index) {makeUseful($(row), index);});
//                        $(".segment").on("select2:select", function(e) {console.log(e.params.data.text)})
        }

    var addListener = function(element, rowIndex) {
            //loop through the html rows and add listeners
            cls = element.attr('class')
            $.each(listeners, function(key, value) {
                if (cls.indexOf(key) > -1) {
                    x = listeners[key](rowIndex)
                    if (element.is('select')){
                        element.on("select2:select", x)
                    } else {
                        element.click(x);
                    }
                }
            });
        }

    var listeners = {
            expand: function(rowId) {
                return function() {
                    rows[rowId].type='filter';
                    rows.push({type: 'newRow'});
                    makeControls();
                }
            },
            newRow: function(rowId) {
                //turn a + button into a breakout
                return function() {
                    rows[rowId].type='breakout';
                    makeControls();
                }
            },
            deleteRow: function(rowId) {
                //remove this row from the controls
                return function() {
                    rows.splice(rowId, 1)
                    makeControls();
                };
            },
            segment: function(rowId) {
                //register the selection
                return function(e) {
                    rows[rowId].segment = e.params.data.id
                }
            },
            logic: function(rowId) {
                return function(e) {
                    rows[rowId].logic = e.params.data.id
                }
            }

        };

    var makeUseful = function(row, rowNum) {
            $.map(row.children(), function(element, indexInRow) {
                element = $(element)
                if (element.is('select')) {
                    if (element.attr('class') == 'segment') {
                        element.select2({
                            data: segments
                        });
                        if (rows[rowNum].segment) {
                            element.val(rows[rowNum].segment).trigger("change")
                        }
                    } else if (element.attr('class') == 'logic') {
                        element.select2({
                            data: logic
                        });
                        if (rows[rowNum].logic) {
                            element.val(rows[rowNum].logic).trigger("change")
                        }
                    } else {
                        element.select2();
                    }
                } 
                addListener(element, rowNum);
            })
        };

    makeControls(); 
    
}

