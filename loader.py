#!flask/bin/python
from app import db, models
from collections import defaultdict
from pprint import pprint
from sqlalchemy import create_engine

import queries

SIGNIFICANT_RECORD_COUNT = 500
SIGNIFICANT_PERCENTILE_ERROR = .15


class RedShiftLoader():

    def __init__(self, endpoint, dbname, port, user, password):
        self.cursor = None
        self.engine_string = "postgresql+psycopg2://%s:%s@%s:%d/%s" % (
            user, password, endpoint, port, dbname)
        self.SIGNIFICANT_RECORD_COUNT = 500
        self.SIGNIFICANT_PERCENTILE_ERROR = .15

    def Connect(self):
        redshift = create_engine(self.engine_string)
        self.cursor = redshift.connect()

    def Query(self, query):
        if not self.cursor:
            self.Connect()

        """hard coded for now"""
        # handle query somehow? 
        rs_query = queries.redshift_query.format(start_date='2015-11-02', end_date='2015-11-06', cid=3521, limit=50000)
        self.rows = self.cursor.execute(rs_query).fetchall()
        print 'query complete', "%i rows returned" % len(self.rows)

    def ReduceResults(self):
        hash_grouped = {}
        id_keys = ['network', 'geo', 'url_domain', 'content_type', 'size']

        for row in self.rows:
            hash_string = "&".join(["=".join([key, row[key]]) for key in id_keys])
            tpclass = row['class']
            # hash_info = hash_grouped.get(hash_string, {})
            exists = hash_grouped.get(hash_string, False)
            if not exists:
                hash_info = {'id':{}, 'metrics':{}, 'count': 0}
                for key in id_keys:
                    hash_info['id'].update({key: row[key]})
                hash_grouped[hash_string] = hash_info

            hash_grouped[hash_string]['count'] += row['bin_count']
            class_exists = hash_grouped[hash_string]['metrics'].get(tpclass, False)
            if class_exists:
                #merge bins into existing descriptor
                hash_grouped[hash_string]['metrics'][tpclass]['bins'].update({row['bin']: row['bin_count']})
                hash_grouped[hash_string]['metrics'][tpclass]['count'] += row['bin_count']
            else:
                #create new class entries
                class_info = {
                                 'bins': {
                                     row['bin'] : row['bin_count']
                                 },
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

                hash_grouped[hash_string]['metrics'][row['class']] = class_info

        self.comparables = self.FinalForm(self.SignificantChecks(hash_grouped))

    def CheckSampleSize(self, comparable):
        return comparable['num_comparable_records'] >= self.SIGNIFICANT_RECORD_COUNT

    def CheckSizePrecision(self, comparable):
        byp = comparable.get('byp', {})
        acc = comparable.get('acc', {})

        checks = [((byp.get(perc, None) - acc.get(perc, None)) / byp[perc]) <
                  SIGNIFICANT_PERCENTILE_ERROR for perc in ['size_25', 'size_50', 'size_75']]
        # print 'checks', checks
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

            if 'acc' in comparable and 'byp' in comparable:
                comparable['comparability'] = all(
                    [self.CheckSampleSize(comparable), self.CheckSizePrecision(comparable)])
            else:
                comparable['comparability'] = False

            comparables.append(comparable)
        pprint(comparables[-50:])
        exit()
        return comparables

    def FinalForm(self, comparable_list):
        reduced_comparables = []
        for comparable in comparable_list:
            reduced = {
                'network': comparable['id']['network'],
                'geo': comparable['id']['geo'],
                'url_domain': comparable['id']['url_domain'],
                'content_type': comparable['id']['content_type'],
                'size': comparable['id']['size'],
                'num_total_records': comparable['num_total_records'],
                'num_comparable_records': comparable['num_comparable_records'],
                'num_exception_records': comparable['num_exception_records'],
                'comparability': comparable['comparability'],
            }
            if comparable['comparability']:
                gain = comparable['byp']['dcu'] / comparable['acc']['dcu'] - 1
            else:
                gain = 0
            reduced.update({'gain': gain})
            reduced_comparables.append(reduced)

        return reduced_comparables

    def LoadToProduction(self):
        for entry in self.comparables[:10]:
            print entry
            #rr = models.ReducedRow(**entry)
            #db.session.add(rr)
        #db.session.commit()

    def Test(self):
        if not self.cursor:
            self.Connect()
        self.Query('huh')

if __name__ == "__main__":
    import credentials
    tplog = RedShiftLoader(credentials.redshift_endpoint, credentials.redshift_dbname,
                           credentials.redshift_port, credentials.redshift_user, credentials.redshift_pass)
    tplog.Query('blah')
    tplog.ReduceResults()
    tplog.LoadToProduction()
    #tplog.Test()
    #for row in tplog.rows[:20]:
    #    print row['bin']
'''
to_print = []
for key, value in comps.iteritems():
        if not value.get('num_records', False):
                print 'oops?', value
        else:
                to_print.append({key: value})
print 'to_print', to_print
pprint(sorted(to_print, key=lambda x: x['num_records'], reverse=True)) 
#for row in prod_results:
#    print row'''
