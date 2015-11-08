#!flask/bin/python
from app import db, models
from collections import defaultdict
from pprint import pprint
from sqlalchemy import create_engine

import json
import utils

class RedShiftLoader():

    def __init__(self, endpoint, dbname, port, user, password):
        self.cursor = None
        self.engine_string = "postgresql+psycopg2://%s:%s@%s:%d/%s" % (
            user, password, endpoint, port, dbname)
        self.SIGNIFICANT_RECORD_COUNT = 50
        self.SIGNIFICANT_PERCENTILE_ERROR = .15

    def Connect(self):
        redshift = create_engine(self.engine_string)
        self.cursor = redshift.connect()

    def Query(self, details):
        if not self.cursor:
            self.Connect()
        
        formatter = self.queryScrub(details) 
        rs_query = utils.redshift_query.format(**formatter)
        self.rows = self.cursor.execute(rs_query).fetchall()
        print 'query complete', "%i rows returned" % len(self.rows)

    def queryScrub(self, details):
        if 'cid' not in details:
            exit('specify cid')
        else:
            self.cid = details['cid']

        scrubbed = {
            'cid': details['cid'],
            'start_date': details.get('start_date', '2015-11-07'),
            'end_date': details.get('end_date', '2015-11-09'),
            'limit': details.get('limit', 500)
            }
        return scrubbed

    def ReduceResults(self):
        hash_grouped = {}
        id_keys = ['network', 'geo', 'url_domain', 'size'] #treat content_type separately
        self.to_add = set()

        for row in self.rows:
            hash_string = "&".join(["=".join([key, row[key]]) for key in id_keys])
            reduced_content = utils.reducedContentType(row['content_type']) 
            if reduced_content == "oops":
                self.to_add.add(row['content_type'])
            hash_string += '&content_type={}'.format(reduced_content)
            tpclass = row['class']
            # hash_info = hash_grouped.get(hash_string, {})
            exists = hash_grouped.get(hash_string, False)
            if not exists:
                hash_info = {'id':{}, 'metrics':{}, 'count': 0}
                for key in id_keys:
                    hash_info['id'].update({key: row[key]})
                hash_info['id'].update({'content_type': reduced_content})
                hash_grouped[hash_string] = hash_info

            hash_grouped[hash_string]['count'] += row['bin_count']
            class_exists = hash_grouped[hash_string]['metrics'].get(tpclass, False)
            if class_exists: 
                hash_grouped[hash_string]['metrics'][tpclass]['count'] += row['bin_count']
                if tpclass in ['acc', 'byp']:
                    #merge bins into existing descriptor
                    hash_grouped[hash_string]['metrics'][tpclass]['bins'].update({row['bin']: row['bin_count']})
            else:
                #create new class entries
                class_info = {
                                 'medians': {
                                     'fbu': row['fbu'], 
                                     'dcu': row['dcu']
                                 },
                                 'sizes': {
                                     'size_25': row['size_25'],
                                     'size_50': row['size_50'],
                                     'size_75': row['size_75']
                                 },
                                 'count': row['bin_count']
                             }
                if tpclass in ['acc', 'byp']:
                    class_info.update({'bins': { row['bin']: int(row['bin_count']) }}) #cast to int so it can be json serialized later

                hash_grouped[hash_string]['metrics'][row['class']] = class_info

        self.comparables = self.FinalForm(self.SignificantChecks(hash_grouped))

    def CheckSampleSize(self, comparable):
        return comparable['num_comparable_records'] >= self.SIGNIFICANT_RECORD_COUNT

    def CheckSizePrecision(self, comparable):
        byp_sizes = comparable['metrics'].get('byp', {}).get('sizes', {})
        acc_sizes = comparable['metrics'].get('acc', {}).get('sizes', {})
        if not acc_sizes and byp_sizes:
            checks=[False]
        else:
            checks = [((byp_sizes[perc] - acc_sizes[perc]) / byp_sizes[perc]) <
                  self.SIGNIFICANT_PERCENTILE_ERROR for perc in ['size_25', 'size_50', 'size_75']]
        return all(checks)

    def SignificantChecks(self, hash_grouped):
        """{}{}{}{}{} reformulate for new metrics object {}{}{}{}{}"""
        comparables = []
        for hashid, comparable in hash_grouped.iteritems():
            num_comp = sum([comparable['metrics'].get(tpclass, {}).get('count', 0)
                            for tpclass in ['acc', 'byp']])
            num_except = sum([comparable['metrics'].get(tpclass, {}).get('count', 0) for tpclass in ['ace', 'bye']])
            comparable['num_comparable_records'] = num_comp
            comparable['num_exception_records'] = num_except
            comparable['num_total_records'] = sum([num_comp, num_except])

            if 'acc' in comparable['metrics'] and 'byp' in comparable['metrics']:
                if self.CheckSampleSize(comparable):
                    if self.CheckSizePrecision(comparable):
                        comparable['comparability'] = True
                    else:
                        comparable['comparability'] = False
                        comparable['fail_reason'] = 'size comparison'
                else:
                    comparable['comparability'] = False
                    comparable['fail_reason'] = 'sample size'
            else:
                comparable['comparability'] = False
                comparable['fail_reason'] = 'acc/byp samples'

            comparables.append(comparable)
        return comparables

    def FinalForm(self, comparable_list):
        reduced_comparables = []

        goods, bads = [], []
        for comparable in comparable_list:
            reduced = {
                'cid': self.cid,
                'network': comparable['id']['network'],
                'geo': comparable['id']['geo'],
                'url_domain': comparable['id']['url_domain'],
                'content_type': comparable['id']['content_type'],
                'size': comparable['id']['size'],
                'num_total_records': comparable['num_total_records'],
                'num_comparable_records': comparable['num_comparable_records'],
                'num_exception_records': comparable['num_exception_records'],
                'comparability': comparable['comparability'],
                'fail_reason': comparable.get('fail_reason', None)
                }
            
            byp_metrics, acc_metrics = comparable['metrics'].get('byp', {}), comparable['metrics'].get('acc', {})
            bins = {
                'acc': acc_metrics.get('bins', {}),
                'byp': byp_metrics.get('bins', {})
                }
            percentiles = {
                'acc': {
                    'dcu_median': float(acc_metrics.get('medians', {}).get('dcu', 0))
                    },
                'byp': {
                    'dcu_median': float(byp_metrics.get('medians', {}).get('dcu', 0))
                    }
                }

            reduced.update({'percentiles': json.dumps(percentiles), 'bins': json.dumps(bins)})

            if comparable['comparability']:
                gain = comparable['metrics']['byp']['medians']['dcu'] / comparable['metrics']['acc']['medians']['dcu'] - 1
                goods.append(comparable)
            else:
                gain = None
                bads.append(comparable)
            reduced.update({'gain': gain})
            reduced_comparables.append(reduced)
        return reduced_comparables

    def LoadToProduction(self):
        for entry in self.comparables: 
            rr = models.ReducedRow(**entry)
            db.session.add(rr)
        db.session.commit()

    def Test(self):
        if not self.cursor:
            self.Connect()
        self.Query('huh')

if __name__ == "__main__":
    import credentials
    import sys
    
    cid = sys.argv[1]
    start = str(sys.argv[2])
    end = str(sys.argv[3])

    tplog = RedShiftLoader(credentials.redshift_endpoint, credentials.redshift_dbname,
                           credentials.redshift_port, credentials.redshift_user, credentials.redshift_pass)
    tplog.Query({'cid': cid, 'start_date': start, 'end_date': end, 'limit': 500000})
    tplog.ReduceResults()
    tplog.LoadToProduction()
    #tplog.Test()
    #for row in tplog.rows[:20]:
    #    print row['bin']
