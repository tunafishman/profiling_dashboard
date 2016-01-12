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
