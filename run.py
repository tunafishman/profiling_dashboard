#!flask-venv/bin/python
from app import app
app.run(host=app.config.get('HOST', 'localhost'))
