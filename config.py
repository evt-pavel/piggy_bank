import os

# команда которая создает абсолютный путь к папке в которой лежит этот файл
# dirname - название директории в которой лежит файл
# abspath - абсолютный путь до жтой дериктории
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = 'firefire'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATION = False

