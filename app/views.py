from app import app, models
from flask import jsonify

@app.route('/')
@app.route('/index')
def index():
	return "Hello World"

@app.route('/api/v1/comparables/')
def comparables():
	passing_comparables = models.ReducedRow.query.filter_by(comparability="True")
	hashes = []
	id_keys = ['network', 'geo', 'url_domain', 'size']
	for entry in passing_comparables.all():
		print type(entry), entry
		hashes.append(entry.network)
	return jsonify({'comparables': hashes})	
