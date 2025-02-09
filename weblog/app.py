from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_migrate import Migrate

from .handlers import blueprint_list
from .configs import configs
from .models import db, Role, User

def register_blueprints(app):
    for bp in blueprint_list:
        app.register_blueprint(bp)


def register_extensions(app):
    Bootstrap(app)
    db.init_app(app)
    Moment(app)  # 现在 Moment 也注册到 Flask 了
    Migrate(app, db)


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(configs.get(config))

    register_extensions(app)
    register_blueprints(app)
    
    return app 

