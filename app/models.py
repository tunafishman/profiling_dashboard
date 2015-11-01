from app import db

class ReducedRow(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	network = db.Column(db.String(6))
	geo = db.Column(db.String(12))
	url_domain = db.Column(db.String(50))
	size = db.Column(db.String(9))
	acc_dcu_median = db.Column(db.Integer)
	byp_dcu_median = db.Column(db.Integer)

	def __repr__(self):
		return '<network %r><geo %r><size %r>' % ( self.network, self.geo, self.size )
"""
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
"""
#def Comparable(
