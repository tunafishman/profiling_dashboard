#!flask/bin/python 
from app import db, models
from collections import defaultdict
from pprint import pprint
from sqlalchemy import create_engine

SIGNIFICANT_RECORD_COUNT = 500
SIGNIFICANT_PERCENTILE_ERROR = .15


class RedShiftLoader():
        
        def __init__(self, endpoint, dbname, port, user, password):
                self.cursor = None
                self.engine_string = "postgresql+psycopg2://%s:%s@%s:%d/%s" % ( user, password, endpoint, port, dbname )
                self.SIGNIFICANT_RECORD_COUNT = 500
                self.SIGNIFICANT_PERCENTILE_ERROR = .15

        def Connect(self):
                redshift = create_engine(self.engine_string)
                self.cursor = redshift.connect()

        def Query(self, query):
                if not self.cursor:
                    self.Connect()
                
                """hard coded for now"""
                #handle query somehow?
                rs_query = '''select
        network,
        size,
        median_dcu,
        json_object_agg(to_char("bucket", '9999'), "bucket_count"),
        sum(bucket_count) 
from (
        select
                partition1 as network,
                partition2 as size,
                max(median_dcu) as median_dcu,
                floor(dcu/100)*100 as bucket,
                count(*) as bucket_count
        from (
                select
                        network as partition1,
                        case when size < 100000 then 'Small' else 'Large' end as partition2,
                        percentile_cont(.50) within
                                group (order by dcu) over (
                                        partition by
                                                network,
                                                case when size < 100000 then 'Small' else 'Large' end
                                ) as median_dcu,
                        dcu
                from 
                        tplog) as t
        group by
                network,
                size,
                bucket
        ) as v
group by
        network,
        size'''
                #rs_query = """select partition1 as network, partition2 as geo, partition3 as url_domain, partition4 as size, count(*) as count, class, max(median_speed) as speed, max(median_fbu) as fbu, max(median_dcu) as dcu, max(extra0) as size_25, max(extra1) as size_50, max(extra2) as size_75, json_obj_agg("bin", "bin_count") from (select network as partition1, geo as partition2, url_domain as partition3, case when size < 10000 then 'Small' when size < 30000 then 'Medium' when size < 50000 then 'Medium+' when size < 200000 then 'Large' else 'X-Large' end as partition4, class, median(speed) over (partition by network, geo, url_domain, case when size < 10000 then 'Small' when size < 30000 then 'Medium' when size < 50000 then 'Medium+' when size < 200000 then 'Large' else 'X-Large' end, class) as median_speed, median(fbu) over (partition by network, geo, url_domain, case when size < 10000 then 'Small' when size < 30000 then 'Medium' when size < 50000 then 'Medium+' when size < 200000 then 'Large' else 'X-Large' end, class) as median_fbu, median(dcu) over (partition by network, geo, url_domain, case when size < 10000 then 'Small' when size < 30000 then 'Medium' when size < 50000 then 'Medium+' when size < 200000 then 'Large' else 'X-Large' end, class) as median_dcu, percentile_cont(0.25) within group (order by size) over (partition by network, geo, url_domain, case when size < 10000 then 'Small' when size < 30000 then 'Medium' when size < 50000 then 'Medium+' when size < 200000 then 'Large' else 'X-Large' end, class) as extra0, median(size) over (partition by network, geo, url_domain, case when size < 10000 then 'Small' when size < 30000 then 'Medium' when size < 50000 then 'Medium+' when size < 200000 then 'Large' else 'X-Large' end, class) as extra1, percentile_cont(0.75) within group (order by size) over (partition by network, geo, url_domain, case when size < 10000 then 'Small' when size < 30000 then 'Medium' when size < 50000 then 'Medium+' when size < 200000 then 'Large' else 'X-Large' end, class) as extra2, floor(dcu/50)*50 as bin, count(*) as bin_count from tplog where datetime > '2015-10-31' and cid = 3521 and network is not null  and geo is not null  and url_domain is not null  and size is not null ) as nested  group by network, geo, url_domain, size, class order by network, geo, url_domain, size, class limit 50000;"""
                self.rows = self.cursor.execute(rs_query)

        def ReduceResults(self):
                hash_grouped = {}
                id_keys = ['network', 'geo', 'url_domain', 'size']
                measurement_keys = ['fbu', 'dcu', 'count', 'size_25', 'size_50', 'size_75']

                for row in self.rows:
                        hash_string = "&".join(["=".join([key, row[key]]) for key in id_keys])
                        exists = hash_grouped.get(hash_string, False) #hash_info = hash_grouped.get(hash_string, {})
                        if not exists:
                                hash_info = {}
                                for key in id_keys:
                                        hash_info.update({key: row[key]})
                                hash_grouped[hash_string] = hash_info
                        
                        class_info = {}
                        for key in measurement_keys:
                                class_info.update({key: row[key]})
                        hash_grouped[hash_string][row['class']] = class_info 

                self.comparables = self.FinalForm(self.SignificantChecks(hash_grouped))

        def CheckSampleSize(self, comparable):
                return comparable['num_comparable_records'] >= self.SIGNIFICANT_RECORD_COUNT    

        def CheckSizePrecision(self, comparable):
                byp = comparable.get('byp', {})
                acc = comparable.get('acc', {})

                checks = [ ( (byp.get(perc, None) - acc.get(perc, None) ) / byp[perc] ) < SIGNIFICANT_PERCENTILE_ERROR for perc in ['size_25', 'size_50', 'size_75']]
                #print 'checks', checks
                return all(checks)

        def SignificantChecks(self, hash_grouped):
                comparables = []
                for hashid, comparable in hash_grouped.iteritems():
                        num_comp = sum([comparable.get(tpclass, {}).get('count', 0) for tpclass in ['acc', 'byp']])
                        num_except = sum([comparable.get(tpclass, {}).get('count', 0) for tpclass in ['ace', 'bye']])
                        comparable['num_comparable_records'] = num_comp
                        comparable['num_exception_records'] = num_except
                        comparable['num_total_records'] = sum([num_comp, num_except])

                        if 'acc' in comparable and 'byp' in comparable:
                                comparable['comparability'] = all([self.CheckSampleSize(comparable), self.CheckSizePrecision(comparable)])
                        else:
                                comparable['comparability'] = False
                        
                        comparables.append(comparable)
                
                return comparables
        
        def FinalForm(self, comparable_list):
                reduced_comparables = []
                for comparable in comparable_list:
                        reduced = {
                                'network': comparable['network'],
                                'geo': comparable['geo'],
                                'url_domain': comparable['url_domain'],
                                'size': comparable['size'],
                                'num_total_records': comparable['num_total_records'],
                                'num_comparable_records': comparable['num_comparable_records'],
                                'num_exception_records': comparable['num_exception_records'],
                                'comparability': comparable['comparability']
                        }
                        if comparable['comparability']:
                                gain = comparable['acc']['dcu']
                        else:
                                gain = 0
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
        tplog = RedShiftLoader(credentials.redshift_endpoint,credentials.redshift_dbname,credentials.redshift_port,credentials.redshift_user,credentials.redshift_pass)
        #tplog.Query('blah')
        #tplog.ReduceResults()
        #tplog.LoadToProduction()
        tplog.Test()
        for row in tplog.rows:
                print row
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
