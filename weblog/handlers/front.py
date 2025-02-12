from flask import Blueprint, url_for, redirect, flash, abort, request
from flask import render_template, current_app, make_response
from flask_login import login_required, login_user, logout_user, current_user
from datetime import datetime

from ..forms import RegisterForm, LoginForm
from ..models import db, User
from ..email import send_email

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

@front.route('/register', methods = ['POST', 'GET'])
def register():
    '''
    用户注册
    '''
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirm_user_token() # 生成验证 token
        send_email(user, user.email, 'confirm_user', token) # 调用方法 send_email() 发送验证邮件
        flash('恭喜注册成功，请登录', 'success')
        # 重定向至登录页面
        return redirect(url_for('.login'))
    return render_template('register.html', form=form)

@front.route('/login', methods=['POST', 'GET'])
def login():
    '''用户登录'''
    if current_user.is_authenticated:
        flash('你已登录。', 'info')
        return redirect(url_for('.index'))
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash('登录成功，{}'.format(user.name), 'success')
            # 如果当前用户未验证
            if not user.confirmed:
                return redirect(url_for('.unconfirmed_user'))
            # 如果当前用于已验证，跳转到首页
            return redirect(url_for('.index'))
        flash('邮箱或密码错误', 'warning')
    return render_template('login.html', form=form)

@front.route('/logout')
def logout():
    '''退出登录'''
    logout_user()
    flash('您已经退出登录', 'info')
    return redirect(url_for('.index'))

# 由 before_app_request 所装饰的视图函数
# 会在所有请求（包括视图函数不在这个蓝图下的请求）被处理之前执行
# 相当于服务器收到任何请求后，先经过此函数进行预处理
@front.before_app_request
def before_request():
    '''页面请求预处理'''
    # current_user 默认为匿名用户，is_authenticated = False (default)
    # 用户登录后，current_user 为登录用户，is_autheticated = True
    if current_user.is_authenticated:        
        # 未验证的用户登录后要发出 POST 请求的话，让用户先通过验证
        # 如果用户未通过邮箱确认身份，且为 POST 请求
        if not current_user.confirmed and request.method == 'POST':
            # 那么把请求交给 front.unconfirmed_user 函数处理
            return redirect(url_for('front.unconfirmed_user'))
        
@front.route('/unconfirmed_user')
@login_required
def unconfirmed_user():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('.index'))
    return render_template('user/confirm.html')

# 接上一个视图函数，浏览器上点击「重发确认邮件按钮」后，由此函数来处理
@front.route('/repeat_confirm')
@login_required
def resend_confirm_email():
    '''重新发送验证邮件'''
    token = current_user.generate_confirm_user_token()
    send_email(current_user, current_user.email, 'confirm_user', token)
    flash('A new confirmation email has been sent to you by email.', 'info')
    return redirect(url_for('.index'))

# 用户注册之后，先在浏览器上登录，然后使用邮件确认账户的邮箱是否准确
# 新注册用户收到验证邮件后，通过点击邮件中提供的地址请求验证
@front.route('/confirm-user/<token>')
@login_required
def confirm_user(token):
    '''验证用户邮箱'''
    if current_user.confirmed:
        flash('账号已经验证过了！', 'info')
    elif current_user.confirm_user(token):
        flash('账号验证成功！', 'success')
    else:
        flash('验证失败，链接无效', 'danger')
    return redirect(url_for('.index'))

