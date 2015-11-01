@app.route('/')
@app.route('/index', methods=['GET'])
def index():
    return "Hello World"

@app.route('/api/v1.0/comp', methods=['GET'])
def get_comparables():
    return jsonify({'comparables': reduced_rows})
