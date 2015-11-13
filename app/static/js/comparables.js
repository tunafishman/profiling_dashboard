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

function addHist(element) { 
    id = "#" + element.id + " svg"
    nv.addGraph({
        generate: function() {
            var width = element.offsetWidth,
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
                .datum(hist_map(hist))
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
                var width = element.offsetWidth;
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

var new_breakout = [{key: 'gains',values: breakout}]
console.log(new_breakout)

function addBreakout(element) {
    var id = "#" + element.id + " svg"
    nv.addGraph({
        generate: function() {
            var width = element.offsetWidth,
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
                .datum(new_breakout)
                .attr('height', height)
                .transition().duration(0)
                .call(chart);


            return chart;
        },
        callback: function(graph) {
            nv.utils.windowResize(function() {
                var width = element.offsetWidth;
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
