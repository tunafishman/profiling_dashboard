import credentials

SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://%s/%s" % ( credentials.production_endpoint, credentials.production_dbname )
SQLALCHEMY_MIGRATE_REPO = credentials.production_migration
