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
    'network': 'network', 
    'geo': 'geo', 
    'url_domain': 'url_domain', 
    'size': 'size', 
    'content_type': 'content_type'
    }

def queryFilter(base_query, selector_string):
    fq = base_query
    selector_types, error = utils.parseSelector(selector_string)
    if error:
        return {'error': error}

    for expr in selector_types[' = ']:
        print expr
        if 'not' in expr[0]:
            expr[0] = expr[0].split('not')[0].strip()
            print expr
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
    passing_comparables = models.ReducedRow.query.filter_by(cid=cid).filter_by(comparability="True").all()
    hashes = []
    
    for entry in passing_comparables:
        hashes.append(entry.network)
    return jsonify({'comparables': hashes}) 

@app.route('/api/v1/<cid>/gains/breakout/<breakout>')
def gains(cid, breakout):
    starttime = time.time()
    if breakout not in api_breakouts:
        return "Break not my api"
    else:
        breakout = api_breakouts[breakout]

    base = models.ReducedRow.query.filter_by(cid=cid).filter_by(comparability="True")
    filtered = queryFilter(base, request.args.get('selector', ''))
    
    if filtered.get('error', False):
        return jsonify(filtered)
    
    temp = defaultdict(lambda: defaultdict(float))
        
    for entry in filtered['results']:
        subset = getattr(entry, breakout)
        temp[subset]['boltzmann_factor'] += float(entry.gain) * float(entry.num_comparable_records)
        temp[subset]['total'] += float(entry.num_comparable_records)

    total = sum([temp[subset]['total'] for subset in temp.keys()])  
    print 'total records considered: {}'.format(total)
    temp['total'] = total 

    to_return = {}
    for tpslice in filter(lambda x: x not in ['total'], temp.keys()):
        to_return[tpslice] = {
            'label': tpslice,
            'gain': temp[tpslice]['boltzmann_factor'] / temp[tpslice]['total'],
            'portion': temp[tpslice]['total'] / temp['total']
            }
    totaltime = time.time() - starttime
    print totaltime
    return jsonify(to_return)

@app.route('/api/v1/<cid>/histogram/')
def histogram(cid):
    filters = utils.parseSelector(request.args.get('selector', ''))
    comparable_query = request.args.get('comparable', False)
    results = models.ReducedRow.query.filter_by(cid=cid)
    if filters:
        results.filter_by(filters)

    results_agg = defaultdict(Counter)
    for comp in results.all():
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

    return jsonify(results_agg)
