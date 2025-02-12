from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

from .handlers import blueprint_list
from .configs import configs
from .models import db, Role, User

mail = Mail()

def register_blueprints(app):
    for bp in blueprint_list:
        app.register_blueprint(bp)


def register_extensions(app):
    Bootstrap(app)
    db.init_app(app)
    Moment(app)  # 现在 Moment 也注册到 Flask 了
    Migrate(app, db)
    mail.init_app(app)  # 初始化 Flask-Mail

    # 配置 Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader  # 这里加上装饰器
    def user_loader(id):
        # 只有主键 id 才能用 query.get 方法查询
        return User.query.get(id)
    
    # 未登录状态下访问带有权限的页面时：自动跳转到此路由
    login_manager.login_view = 'front.login'
    # 提示信息内容及类型
    login_manager.login_message = '请登录后访问'
    login_manager.login_message_category = 'warning'


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(configs.get(config))

    register_extensions(app)
    register_blueprints(app)
    
    return app 

