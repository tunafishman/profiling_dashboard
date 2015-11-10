from app import app, models, utils
from collections import Counter, defaultdict
from flask import jsonify, request

import json
import time

@app.route('/')
@app.route('/index')
def index():
    return "Hello World"

@app.route('/api/v1/<cid>/comparables/')
def comparables(cid):
    passing_comparables = models.ReducedRow.query.filter_by(cid=cid).filter_by(comparability="True").all()
    hashes = []
    id_keys = ['network', 'geo', 'url_domain', 'size', 'content_type']
    for entry in passing_comparables:
        hashes.append(entry.network)
    return jsonify({'comparables': hashes}) 

@app.route('/api/v1/<cid>/gains/breakout/<breakout>')
def gains(cid, breakout):
    starttime = time.time()
    acceptable_breakouts =  {
                    'network': 0,
                    'geo': 1,
                    'url_domain': 2,
                    'size': 3,
                    'content_type': 4
                    }
    if breakout not in acceptable_breakouts:
        return "Break not my api"
    else:
        case = acceptable_breakouts[breakout]

    results = models.ReducedRow.query.filter_by(cid=cid).filter_by(comparability="True").all()
    temp = defaultdict(lambda: defaultdict(float))
        
    for entry in results:
        if case == 0:
            subset = entry.network
        elif case == 1:
            subset = entry.geo
        elif case == 2:
            subset = entry.url_domain
        elif case == 3:
            subset = entry.size
        elif case == 4:
            subset = entry.content_type   

        temp[subset]['boltzmann_factor'] += float(entry.gain) * float(entry.num_comparable_records)
        temp[subset]['total'] += float(entry.num_comparable_records)

    total = sum([temp[subset]['total'] for subset in temp.keys()])  
    print 'total records considered: {}'.format(total)
    temp['total'] = total 

    to_return = {'results': {}}
    for tpslice in filter(lambda x: x not in ['total'], temp.keys()):
        print tpslice, temp[tpslice]
        to_return['results'][tpslice] = {
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
