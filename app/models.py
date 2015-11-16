from app import db
from sqlalchemy.dialects.postgresql import BOOLEAN, JSON

class ReducedRow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cid = db.Column(db.Integer)
    network = db.Column(db.String(10))
    geo = db.Column(db.String(20))
    url_domain = db.Column(db.String(200))
    size = db.Column(db.String(10))
    content_type = db.Column(db.String(70))
    comparability = db.Column(db.Boolean, default=False)
    gain = db.Column(db.Numeric)
    num_total_records = db.Column(db.Integer)
    num_comparable_records = db.Column(db.Integer)
    num_exception_records = db.Column(db.Integer)
    fail_reason = db.Column(db.String(20))
    bins = db.Column(JSON)
    percentiles = db.Column(JSON)
    reduced_date = db.Column(db.DateTime)

