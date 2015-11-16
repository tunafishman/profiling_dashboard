from app import app, models, utils
from collections import Counter, defaultdict
from flask import jsonify, render_template, request

import json
import time


### pages ###
@app.route('/')
@app.route('/index')
def index():
    return render_template("hero-thirds.html")

@app.route('/test')
def test():
    return render_template("test.html")

@app.route('/bootstrap')
def bootstrap():
    return render_template('bootstrap.html')

### API endpoints ###
api_breakouts = {
    '': None,
    'network': 'network', 
    'geo': 'geo', 
    'url_domain': 'url_domain', 
    'size': 'size', 
    'content_type': 'content_type'
    }

def queryFilter(base_query, selector_string):
    ''' this takes in a selector from a GET param and returns records that meet the selectors '''
    fq = base_query
    selector_types, error = utils.parseSelector(selector_string)
    if error:
        return {'error': error}

    for expr in selector_types[' = ']:
        print expr
        if 'not' in expr[0]:
            expr[0] = expr[0].split('not')[0].strip()
            fq = fq.filter(getattr(models.ReducedRow, expr[0]) != expr[1])
        else:
            fq = fq.filter(getattr(models.ReducedRow, expr[0]) == expr[1])
    for expr in selector_types[' like ']:
        if 'not' in expr[0]:
            expr[0] = expr[0].split('not')[0].strip()
            fq = fq.filter(~getattr(models.ReducedRow, expr[0]).like("%%{}%%".format(expr[1])))
        else:
            fq = fq.filter(getattr(models.ReducedRow, expr[0]).like("%%{}%%".format(expr[1])))

    for expr in selector_types[' in ']:
        print expr, type(expr[1])
        if 'not' in expr[0]:
            expr[0] = expr[0].split('not')[0].strip()
            fq = fq.filter(~getattr(models.ReducedRow, expr[0]).in_(expr[1]))
        else:
            fq = fq.filter(getattr(models.ReducedRow, expr[0]).in_(expr[1]))

    return {'results': fq.all()}

@app.route('/api/v1/<cid>/comparables/')
def comparables(cid):
    details = request.args
    breakout = details.get('breakout', '')

    if breakout not in api_breakouts:
        return "Break not my api"
    else:
        breakout = api_breakouts[breakout]

    comp = details.get('comparable', 'false').lower() == 'true'
    selector = details.get('selector', '')

    base = models.ReducedRow.query.filter_by(cid=cid)
    if comp:
        base.filter_by(comparability="True")

    filtered = queryFilter(base, selector)
    
    if filtered.get('error', False):
        return jsonify(filtered)
    
    results_agg = defaultdict(int)
    for entry in filtered['results']:
        if breakout:
            subset = getattr(entry, breakout)
        else:
            subset = 'global'

        if comp:
            num = entry.num_comparable_records
            results_agg[subset] += num
        else:
            num = entry.num_total_records
            results_agg[subset] += num

    total = sum([v for k, v in results_agg.iteritems()])
    results_agg = [{'label': k, 'value': float(v)/total} for k, v in results_agg.iteritems()]

    print results_agg
        
    return jsonify({'key': 'comparables', 'values': results_agg}) 

@app.route('/api/v1/<cid>/gains/')
def gains(cid):
    starttime = time.time()

    details = request.args
    breakout = details.get('breakout', '')

    if breakout not in api_breakouts:
        return "Break not my api"
    else:
        breakout = api_breakouts[breakout]

    base = models.ReducedRow.query.filter_by(cid=cid).filter_by(comparability="True")
    filtered = queryFilter(base, details.get('selector', ''))
    
    if filtered.get('error', False):
        return jsonify(filtered)
    
    temp = defaultdict(lambda: defaultdict(float))
        
    for entry in filtered['results']:
        if breakout:
            subset = getattr(entry, breakout)
        else:
            subset = 'global'

        print subset
        temp[subset]['boltzmann_factor'] += float(entry.gain) * float(entry.num_comparable_records)
        temp[subset]['total'] += float(entry.num_comparable_records)

    total = sum([temp[subset]['total'] for subset in temp.keys()])  
    print 'total records considered: {}'.format(total)
    temp['total'] = total 

    to_return = []
    for tpslice in filter(lambda x: x not in ['total'], temp.keys()):
        temp_return = {
            'label': tpslice,
            'value': temp[tpslice]['boltzmann_factor'] / temp[tpslice]['total'],
            'portion': temp[tpslice]['total'] / temp['total']
            }
        to_return.append(temp_return)
    totaltime = time.time() - starttime
    print totaltime
    return jsonify({'key': 'gains', 'values': to_return})

@app.route('/api/v1/<cid>/histogram/')
def histogram(cid):
    starttime = time.time()
    details = request.args
    selector = details.get('selector', '')
    comparable_query = request.args.get('comparable', False)

    base_query  = models.ReducedRow.query.filter_by(cid=cid)
    filtered = queryFilter(base_query, selector)

    if filtered.get('error', False):
        return jsonify(filtered)
    totals = defaultdict(int)
    results_agg = defaultdict(Counter)
    for comp in filtered['results']:
        temp = {}
        comp_bins = json.loads(comp.bins)
        temp['byp'] = Counter(comp_bins.get('byp', {}))
        if comparable_query:
            #aggregate acc and byp where appropriate
            if comp.comparability:
                temp['acc'] = Counter(comp_bins.get('acc', {}))
        #else aggregate byp only

        for tpclass in temp:
            results_agg[tpclass] += temp[tpclass]

    to_return = []
    for tpclass in results_agg:
        #grab total
        total = sum([v for k, v in results_agg[tpclass].iteritems()]) 
        temp_series = [ {'x': int(bucket), 'y': float(bucket_hits) / total} for bucket, bucket_hits in results_agg[tpclass].iteritems() if bucket != ">4000"]
        to_return.append({'key': tpclass, 'values': temp_series})

    duration = time.time() - starttime
    print duration

    return jsonify({'histograms': to_return})
