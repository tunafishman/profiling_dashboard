from app import db
from sqlalchemy.dialects.postgresql import BOOLEAN

class ReducedRow(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	network = db.Column(db.String(10))
	geo = db.Column(db.String(20))
	url_domain = db.Column(db.String(200))
	size = db.Column(db.String(10))
	comparability = db.Column(db.Boolean, default=False)
	gain = db.Column(db.Numeric)
	num_total_records = db.Column(db.Integer)
	num_comparable_records = db.Column(db.Integer)
	num_exception_records = db.Column(db.Integer)

	def __repr__(self):
		return str({
			'network': self.network,
			'geo': self.geo,
			'size': self.size,
			'url_domain': self.url_domain,
			'comparability': self.comparability,
			'measurements': {
					'gain': self.gain,
					'num_total_records': self.num_total_records,
					'num_comparable_records': self.num_comparable_records,
					'num_exception_records': self.num_exception_records
					}
			})
'''
{'comparability': False,
  'geo': u'us-west-3',
  'network': u'3G',
  'num_comparable_records': 6L,
  'num_exception_records': 1L,
  'num_total_records': 7L,
  'size': u'Small',
  'url_domain': u'fratello.disqus.com'}

reduced_rows = [
    {
        "geo": "us-west-1",
        "network": "WiFi",
        "url_domain": "www.google.com",
        "size": "Small",
        "dcu": [100, 200, 30, 10, 0]
    },
    {
        "geo": "us-east-2",
        "network": "LTE",
        "url_domain": "www.hsn.com", 
        "size": "Large",
        "dcu": [20, 140, 70, 20, 5]
    }
]
'''
#def Comparable(
