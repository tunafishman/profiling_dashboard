function api_query(cid, endpoint, args) {
    base_url = "http://localhost:5001/api/v1/"

    if (!(endpoint == 'gains' || endpoint == 'histogram' || endpoint == 'comparables')) { return {} }

    api_url = base_url + cid + '/' + endpoint + '/'
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
    plottable.push(temp)
    return plottable
}

function hist_map(api_hist) {
    plottable = []
    for (entry in api_hist) {
        temp = {key: api_hist[entry].key, values: api_hist[entry].values.sort(function(a,b){return a.x - b.x})}
        plottable.push(temp)
    }

    console.log(plottable)

    return plottable
}

function gain_map(api_gain) {
    console.log('gain_map');
    var series = []

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

            var chart = nv.models.multiBarChart()
                .width(width)
                .height(height)
                .stacked(false)
                .showControls(false)
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
