from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from pyngrok import ngrok


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
moment = Moment()
bootstrap = Bootstrap()
login.login_view = 'auth.login'
login.login_message = "You must be logged in to visit that page!"
#декоратор @login_required и еще его надо импортировать


def create_app(class_config=Config):

    app = Flask(__name__)
    # port = 5000
    # public_url = ngrok.connect(port).public_url
    # print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    moment.init_app(app)
    bootstrap.init_app(app)


    from app.main import main
    app.register_blueprint(main)

    from app.auth import auth
    app.register_blueprint(auth)

    if __name__ == 'app':
        app.run(host='0.0.0.0')

    return app


from app.auth import routes
