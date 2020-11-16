class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'FLEXPROJECT'
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://admin:admin12345@flexproyect.cqwbrqenmt7b.us-east-2.rds.amazonaws.com/flexProyect"


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