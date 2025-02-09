from flask import Blueprint, render_template
from datetime import datetime

front = Blueprint('front', __name__)

@front.route('/')
def index():
    date_time = datetime.utcnow()
    return render_template('index.html', date_time=date_time)

@front.app_errorhandler(404)
def page_not_found(e):
    '''
    路由错误，不存在该页面
    '''
    return render_template('404.html'), 404

@front.app_errorhandler(500)
def inter_server_error(e):
    '''
    服务器内部错误
    '''
    return render_template('500.html'), 500

