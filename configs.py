class Config(object):
    DEBUG = True
    SERVER_NAME = "localhost:5001"
    API_URL = "localhost"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://localhost/comparables"

class Production(object):
    DEBUG = False
    SERVER_NAME = "web-01:5001"
    API_URL = "web-01:5001"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2:///comparables"
