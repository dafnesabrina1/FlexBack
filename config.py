class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'FLEXPROJECT'
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://admin:admin123@database-1.czw3rvdb7hgc.us-east-2.rds.amazonaws.com/FLEX"


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True