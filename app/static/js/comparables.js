function api_query(cid, endpoint, selector, breakout) {
    base_url = "http://localhost:5001/api/v1/"

    if (!(endpoint == 'gains' || endpoint == 'histogram')) { return {} }

    api_url = base_url + cid + '/' + endpoint + '/?breakout=' + breakout + '&selector=' + selector + '&comparable=true'
    xhr = $.ajax(api_url)

    return xhr
}

function makeGains( id, selector, breakout) {
    console.log(typeof breakout)
    api_query(91, 'gains', selector, breakout).done(function(data){addBreakout(id, data)});
};

function makePopulation( id, selector) {
    console.log(selector);
    api_query(91, 'histogram', selector).done(function(data){addHist( id, data)})
};

function hist_map(api_hist) {
    if (Object.keys(api_hist).length == 0) {
        alert("something happened");
    } else {
        series = []
        Object.keys(api_hist).map(function(tpclass, i) {
            
            this_hist = []
            Object.keys(api_hist[tpclass]).map(function(bucket) {
                obj = {x: parseInt(bucket), y: api_hist[tpclass][bucket]}
                this_hist.push(obj)
            })

            series.push({ key: tpclass, values: this_hist})
        })
    }

    return series
}

function gain_map(api_gain) {
    console.log('gain_map');
    var series = []

    Object.keys(api_gain).map(function(label, i) {
        series.push(api_gain[label])
    });
    console.log(series)
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
                .datum(hist_map(data))
                .attr('width', width)
                .attr('height', height)
                .transition().duration(0)
                .call(chart);
            console.log('calling chart 2');
            console.log(hist_map(hist));

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

function massageGain(data) { return [{key: 'gains',values: data}] }

function addBreakout(id, data) {
    console.log('sad');
    console.log(data)
    var id = id + " svg"
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
                .datum(gain_map(data))
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
