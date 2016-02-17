from app import app, models, utils
from collections import Counter, defaultdict
from flask import jsonify, render_template, request

import copy
import customers
import json
import time

class Timer():

    def __init__(self, name, to_log=False):
        self.start = None
        self.end = None
        self.name = name
        self.to_log = to_log
        self.logfile = 'logs.txt'

    def Start(self):
        self.start = time.time()

    def End(self):
        self.end = time.time()
        self.elapsed = self.end - self.start

    def Printer(self):
        return "{} - {} completed in {} ms\n".format(self.start, self.name, self.elapsed)

    def Log(self):
        with open(self.logfile, 'a') as f:
            f.write(self.Printer())

### pages ###
@app.route('/')
@app.route('/index')
def index():
    details = request.args
    page_state = {
        "cid": details.get("cid", False),
        "selector": details.get("selector", False),
        "breakout": details.get("breakout", False)
    }
    return render_template("dashboard.html", customers = cids(), api_url = app.config['API_URL'], page_state = page_state)

@app.route('/test')
def test():
    details = request.args
    page_state = {
        "cid": details.get('cid', False),
        "selector": details.get('selector', False),
        "breakout": details.get('breakout', False)
        }
    print page_state
    return render_template("test.html", page_state = page_state, customers = cids(), subsets = api_breakouts.keys())

@app.route('/segboxes')
def segboxes():
    return render_template("segboxes.html", customers = cids())

@app.route('/life')
def life():
    details = request.args
    page_state = {
        "cid": details.get("cid", False),
        "selector": details.get("selector", False),
        "breakout": details.get("breakout", False)
    }
    return render_template("lifecycle.html", customers = cids(), api_url = app.config['API_URL'], page_state = page_state)

### API endpoints ###
api_breakouts = {
    '': None,
    'network': 'network', 
    'geo': 'geo', 
    'url_domain': 'url_domain', 
    'size': 'size', 
    'content_type': 'content_type',
    'schema': 'schema',
    'sdk_version': 'sdk_version'
    }

def queryFilter(base_query, selector_string):
    ''' this takes in a selector and returns records that meet the selectors '''
    fq = base_query
    selector_types, error = utils.parseSelector(selector_string)
    if error:
        return {'error': error}

    for expr in selector_types[' = ']:
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
        if 'not' in expr[0]:
            expr[0] = expr[0].split('not')[0].strip()
            fq = fq.filter(~getattr(models.ReducedRow, expr[0]).in_(expr[1]))
        else:
            fq = fq.filter(getattr(models.ReducedRow, expr[0]).in_(expr[1]))

    return {'results': fq.all()}

def cids():
    base = models.db.session.query(models.ReducedRow.cid).distinct().all()
    cids = sorted([item.cid for item in base])
    cidlist = [{'name': customers.cidToName.get(cid, cid), 'cid':cid} for cid in cids]
    return cidlist

@app.route('/api/v1/<cid>/values')
def values(cid):
    details = request.args
    segment = details.get('segment', False) #a segment is required to grab values
    selector = details.get('selector', '')

    if segment not in api_breakouts:
        return "Break not my api"
    else:
        segment = api_breakouts[segment]

    base = models.ReducedRow.query.filter_by(cid=cid)
    filtered = queryFilter(base, selector)

    if filtered.get('error', False):
        return jsonify(filtered)

    results_agg = defaultdict(int)
    for entry in filtered['results']:
        value = getattr(entry, segment)
        results_agg[value] += entry.num_total_records

    return jsonify({'segment': segment, 'total': sum([x[1] for x in results_agg.items()]), 'values': dict(results_agg)})

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
        subset = getattr(entry, breakout) if breakout else 'global'

        if comp:
            num = entry.num_comparable_records
            results_agg[subset] += num
        else:
            num = entry.num_total_records
            results_agg[subset] += num

    total = sum([v for k, v in results_agg.iteritems()])
    results_agg = [{'label': k, 'value': float(v)/total} for k, v in results_agg.iteritems()]

    return jsonify({'key': 'comparables', 'values': results_agg}) 

@app.route('/api/v1/<cid>/gains/')
def gains(cid):
    gain_timer = Timer('gains request')
    gain_timer.Start()

    details = request.args
    breakout = details.get('breakout', '')

    if breakout not in api_breakouts:
        return "Break not my api"
    else:
        breakout = api_breakouts[breakout]
    
    query_timer = Timer('gains query')
    query_timer.Start()
    base = models.ReducedRow.query.filter_by(cid=cid).filter_by(comparability="True")
    filtered = queryFilter(base, details.get('selector', ''))
    query_timer.End()
    query_timer.Log()

    if filtered.get('error', False):
        return jsonify(filtered)

    print "query returned {} comparable segments".format(len(filtered['results']))
   
    temp = defaultdict(lambda: defaultdict(float))
        
    gain_massage = Timer('gains coalesce')
    gain_massage.Start()
    for entry in filtered['results']:
        subset = getattr(entry, breakout) if breakout else 'global'

        temp[subset]['comp_records'] += float(entry.num_comparable_records)
        temp[subset]['total_records'] += float(entry.num_total_records)
        temp[subset]['boltzmann_factor'] += float(entry.gain) * float(entry.num_comparable_records)

    total_comp, total_num = sum([temp[subset]['comp_records'] for subset in temp.keys()]), sum([temp[subset]['total_records'] for subset in temp.keys()])
    print 'total records considered: {}, total records comparable: {}, {}%'.format(total_num, total_comp, 100*total_comp/total_num)
    temp['total_comp_records'] = total_comp
    temp['total_num_records'] = total_num

    to_return = []
    for tpslice in filter(lambda x: x not in ['total_comp_records', 'total_num_records'], temp.keys()):
        temp_return = {
            'label': tpslice,
            'value': temp[tpslice]['boltzmann_factor'] / temp[tpslice]['comp_records'],
            'portion': temp[tpslice]['comp_records'] / temp['total_comp_records'],
            'significance': temp[tpslice]['comp_records'] / temp[tpslice]['total_records']
            }
        to_return.append(temp_return)
    gain_massage.End()
    gain_massage.Log()

    gain_timer.End()
    gain_timer.Log()
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

@app.route('/api/v1/<cid>/lifecycle/')
def lifecycle(cid):
    starttime = time.time()
    details = request.args
    selector = details.get('selector', '')
    breakout = details.get('breakout', '')
    comparable_query = request.args.get('comparable', 'false').lower() == 'true'
    
    if breakout not in api_breakouts:
        return "Break not my api"
    else:
        breakout = api_breakouts[breakout]
    
    perc_base = {'byp': {'fbu': defaultdict(float), 'dcu': defaultdict(float)}}

    base_query = models.ReducedRow.query.filter_by(cid=cid)

    if comparable_query:
        base_query.filter_by(comparability=True)
        perc_base.update({'acc': {'fbu': defaultdict(float), 'dcu': defaultdict(float)}})

    filtered = queryFilter(base_query, selector)

    if filtered.get('error', False):
        return jsonify(filtered)

    results_agg = {}
    for entry in filtered['results']:
        if breakout:
            subset = getattr(entry, breakout)
        else:
            subset = 'total'
  
        if not results_agg.get(subset, False):
            print "Making results for {}".format(subset)
            results_agg[subset] = copy.copy(perc_base)

        percs = json.loads(entry.percentiles)
        
        #check to see if the measurements are there for this comparable
        if not all([percs.get(tpclass, {}) != {} for tpclass in perc_base.keys()]):
            continue
        
        for tpclass in results_agg[subset]:
            for measure in ['fbu', 'dcu']:
                for perc in ['perc25', 'perc50', 'perc75']:
                    key = "_".join([perc, measure])
                    try:
                        results_agg[subset][tpclass][measure][key] += (percs[tpclass][measure][key] * entry.num_comparable_records) 
                        results_agg[subset][tpclass][measure][key + '_total'] += entry.num_comparable_records
                    except:
                        print "I'm not sure what to do with these yet", percs

    to_return = []
    for subset in results_agg:
        percentiles = {'count':0}
        for tpclass in results_agg[subset]:
            percentiles.update({tpclass: {}})
            for measure in ['fbu', 'dcu']:
                percentiles[tpclass][measure] = {}
                for perc in ['perc25', 'perc50', 'perc75']:
                    key = "_".join([perc, measure])
                    try:
                        percentiles[tpclass][measure][key] = results_agg[subset][tpclass][measure][key] / results_agg[subset][tpclass][measure][key + "_total"]
                    except:
                        continue

        to_return.append({subset: percentiles})

    return jsonify({'percentiles': to_return})
