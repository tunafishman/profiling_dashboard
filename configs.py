class Config(object):
    DEBUG = True
    SERVER_NAME = "localhost:5001"
    API_URL = "localhost"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class Production(object):
    DEBUG = False
    SERVER_NAME = "0.0.0.0:5001"
    API_URL = "web-01"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
