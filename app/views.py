from app import app, models
from collections import defaultdict
from flask import jsonify

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
    
    print len(results), case
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
    temp['total'] = total 

    to_return = {'results': {}}
    for key in filter(lambda x: x not in ['total'], temp.keys()):
        to_return['results'][key] = {
            'gain': temp[key]['boltzmann_factor'] / temp[key]['total'],
            'portion': temp[key]['total'] / temp['total']
            }
    totaltime = time.time() - starttime
    print totaltime
    return jsonify(to_return)

