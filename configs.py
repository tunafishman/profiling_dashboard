class Config(object):
    DEBUG = True
    SERVER_NAME = "localhost:5001"
    API_URL = "http://localhost:5001/api/v1"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://localhost/comparables"

class Production(object):
    DEBUG = False
    SERVER_NAME = "web-01:5001"
    API_URL = "http://web-01:5001/api/v1"
    HOST = "0.0.0.0"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2:///comparables"
