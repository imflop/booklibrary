import os


class TestConfig(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'blib.db')
    testing = True
    debug = True
