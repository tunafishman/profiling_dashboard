from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import configs
import os

app = Flask(__name__)

tp_env = os.environ.get('TP_ENV_TYPE', 'dev')
if tp_env == 'prod':
    app.config.from_object(configs.Production)
else:
    app.config.from_object(configs.Config)

db = SQLAlchemy(app)

from app import models, views
