#!flask-venv/bin/python
from app import app

import configs
import os

tp_env = os.environ.get('TP_ENV_TYPE', 'dev')

if tp_env == 'prod':
    app.config.from_object(configs.Production)
else:
    app.config.from_object(configs.Config)

app.run()
