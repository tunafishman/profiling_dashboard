#!flask/bin/python
from app import db, models, utils
from collections import defaultdict
from sqlalchemy import create_engine, text

import datetime
import json
import pyodbc
import sqlalchemy as sa

class VerticaLoader():

    def __init__(self, endpoint, dbname, port, user, password, endpoint_big=None):
        self.cursor = None
        self.endpoint = endpoint
        self.endpoint_big = endpoint_big
        self.dbname = dbname
        self.port = port
        self.user = user
        self.password = password
        self.SIGNIFICANT_RECORD_COUNT = 200
        self.SIGNIFICANT_PERCENTILE_ERROR = .15

    def dbCidMap(self):
        bigs = ['91', '90', '30', '3524']
        if self.cid in bigs:
            return self.endpoint_big
        else:
            return self.endpoint

    def Connect(self):
        self.engine_string = "vertica+pyodbc://{user}:{password}@{endpoint}/{dbname}".format(user=self.user, password=self.password, endpoint=self.dbCidMap(), dbname=self.dbname)
        vertica = sa.create_engine(self.engine_string + '?driver=/Library/Vertica/ODBC/lib/libverticaodbc.dylib')
        self.cursor = vertica.connect()

    def Query(self, cid, start_date='', end_date='', limit=500):
        self.cid = cid
        self.test()

        formatter = self.queryScrub({
            'start_date': start_date,
            'end_date': end_date,
            'limit': limit,
            'cid': cid
            })

        self.currentStart = formatter['start_date']

        vertica_query = utils.redshift_query.format(**formatter)
        self.rows = self.cursor.execute(text(vertica_query)).fetchall()
        print 'query complete', "%i rows returned" % len(self.rows)

    def queryScrub(self, details):
        ''' some day this would check for whether a user had access to this cid '''
        self.cid = details['cid']

        # default to grabbing yesterday's data
        scrubbed = {
            'cid': details['cid'],
            'start_date': details.get('start_date', datetime.date.today() - datetime.timedelta(days=1)).isoformat(),
            'end_date': details.get('end_date', datetime.date.today()).isoformat(),
            'limit': details.get('limit')
            }
        return scrubbed

    def ReduceResults(self):
        hash_grouped = {}
        id_keys = ['network', 'geo', 'url_domain', 'size', 'content_type'] #treat content_type separately

        for row in self.rows:
            hash_string = "&".join(["=".join([key, row[key]]) for key in id_keys])
            tpclass = row['class']
            exists = hash_grouped.get(hash_string, False)
            if not exists:
                hash_info = {'id':{}, 'metrics':{}, 'count': 0}
                for key in id_keys:
                    hash_info['id'].update({key: row[key]})
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
                class_info = {'count': row['bin_count']}
                if tpclass in ['acc', 'byp']:

                    sql_percentiles = ['perc25', 'perc50', 'perc75']
                    sql_measures = ['fbu', 'dcu']
                    percentiles = {}

                    for measure in sql_measures:
                        percentiles[measure] = {}
                        for perc in sql_percentiles:
                            key = '_'.join([perc, measure])
                            if row[key]:
                                percentiles[measure][key] = float(row[key])
                            else:
                                percentiles[measure][key] = None

                    class_details = {
                                        'percentiles': percentiles,
                                         'sizes': {
                                             'size_25': row['size_25'],
                                             'size_50': row['size_50'],
                                             'size_75': row['size_75']
                                         },
                                         'bins': {
                                             row['bin']: int(row['bin_count']) #cast to int so it can be json serialized later
                                         }
                                    }

                    class_info.update(class_details)

                hash_grouped[hash_string]['metrics'][row['class']] = class_info

        print 'sum total of hashes', sum([hash_grouped[subset]['count'] for subset in hash_grouped])

        self.comparables = self.finalForm(self.significantChecks(hash_grouped))

    def checkClasses(self, comparable):
        #do medians exist for both acc and byp?
        return all([ comparable['metrics'].get('byp', False), comparable['metrics'].get('acc', False)])

    def checkSampleSize(self, comparable_count):
        return comparable_count >= self.SIGNIFICANT_RECORD_COUNT

    def checkSizePrecision(self, comparable_metrics):
        byp_sizes = comparable_metrics.get('byp', {}).get('sizes', {})
        acc_sizes = comparable_metrics.get('acc', {}).get('sizes', {})
        if not acc_sizes and byp_sizes:
            checks=[False]
        else:
            try:
                checks = [((byp_sizes[perc] - acc_sizes[perc]) / byp_sizes[perc]) <
                    self.SIGNIFICANT_PERCENTILE_ERROR for perc in ['size_25', 'size_50', 'size_75']]
            except:
                print "line 133", comparable_metrics
                checks = [False]
        return all(checks)

    def significantChecks(self, hash_grouped):
        comparables = []
        for hashid, comparable in hash_grouped.iteritems():
            num_comp = sum([comparable['metrics'].get(tpclass, {}).get('count', 0)
                            for tpclass in ['acc', 'byp']])
            num_except = sum([comparable['metrics'].get(tpclass, {}).get('count', 0) for tpclass in ['ace', 'bye']])
            comparable['num_comparable_records'] = num_comp
            comparable['num_exception_records'] = num_except
            comparable['num_total_records'] = sum([num_comp, num_except])

            if self.checkClasses(comparable):
                if self.checkSampleSize(comparable['num_comparable_records']):
                    if self.checkSizePrecision(comparable['metrics']):
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

    def finalForm(self, comparable_list):
        reduced_comparables = []

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
                'fail_reason': comparable.get('fail_reason', None),
                'reduced_date': self.currentStart
                }

            byp_metrics, acc_metrics = comparable['metrics'].get('byp', {}), comparable['metrics'].get('acc', {})
            bins = {
                'acc': acc_metrics.get('bins', {}),
                'byp': byp_metrics.get('bins', {})
                }
            percentiles = {
                'acc': acc_metrics.get('percentiles', {}),
                'byp': byp_metrics.get('percentiles', {})
                }

            reduced.update({'percentiles': json.dumps(percentiles), 'bins': json.dumps(bins)})

            if comparable['comparability']:
                gain = float(percentiles['byp']['dcu']['perc50_dcu']) / float(percentiles['acc']['dcu']['perc50_dcu']) - 1
            else:
                gain = None
            reduced.update({'gain': gain})
            reduced_comparables.append(reduced)
        return reduced_comparables

    def LoadToProduction(self):
        print "Adding {} comparables to reduced_row".format(len(self.comparables))
        for entry in self.comparables:
            rr = models.ReducedRow(**entry)
            db.session.add(rr)
        db.session.commit()

    def DailyJobs(self, cid, num_days, end=datetime.datetime.now()):
        ''' create a set of jobs to process for daily aggregation '''
        print "Grabbing the last {} days for cid {}".format(num_days, cid)
        today = datetime.date.today()
        dates = [ (today - datetime.timedelta(days=n), today - datetime.timedelta(days=n+1)) for n in range(0, num_days) ]

        for job in dates:
            self.Query( cid, job[1], job[0], 500000)
            self.ReduceResults()
            self.LoadToProduction()

            self.rows, self.comparables = None, None

    def test(self):
        if not self.cursor:
            self.Connect()

if __name__ == "__main__":
    import credentials
    import sys

    cid = sys.argv[1]
    num_days = int(sys.argv[2])

    tplog = VerticaLoader(credentials.vertica_endpoint, credentials.vertica_dbname,
                            credentials.vertica_port, credentials.vertica_user, credentials.vertica_pass, endpoint_big  = credentials.vertica_endpoint_big)

    tplog.DailyJobs(cid, num_days)
