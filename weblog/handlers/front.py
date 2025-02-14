from flask import Blueprint, url_for, redirect, flash, abort, request
from flask import render_template, current_app, make_response
from flask_login import login_required, login_user, logout_user, current_user
from datetime import datetime

from ..forms import RegisterForm, LoginForm, BlogForm
from ..models import db, User, Blog
from ..email import send_email

front = Blueprint('front', __name__) # front.py - 主页相关

@front.route('/', methods=['GET', 'POST'])
def index():
    '''主页'''
    date_time = datetime.utcnow()
    form = BlogForm()
    # 只要用户登录成功，就可以发表博客
    if current_user.is_authenticated and form.validate_on_submit():
        blog = Blog()
        form.populate_obj(blog)
        blog.author = current_user
        db.session.add(blog)
        db.session.commit()
        flash('发表成功', 'success')
        return redirect(url_for('.index'))
    # 从 URL 参数中获取页码，默认为第 1 页
    # 例如：/?page=2，如果没有 page 参数则返回 1
    page = request.args.get('page', 1, type=int)

    # 使用 SQLAlchemy 的 paginate 方法进行分页查询
    pagination = Blog.query.order_by(Blog.time_stamp.desc()).paginate(
            page=page,  # 当前页码
            per_page=current_app.config['BLOGS_PER_PAGE'],  # 每页显示的博客数量
            error_out=False  # 当页码超出范围时不报错，而是返回空列表
    )

    # 获取当前页的博客列表
    blogs = pagination.items

    # 将分页对象和博客列表传递给模板
    return render_template('index.html', 
                         form=form,  # 发博客的表单
                         blogs=blogs,  # 当前页的博客列表
                         pagination=pagination)  # 分页对象，用于生成分页导航

@front.route('/blog/<int:id>')
def blog(id):
    '''博客详情页'''
    blog = Blog.query.get_or_404(id)
    # hidebloglink 为布尔值，用于隐藏博客详情页的链接
    # noblank 为布尔值，用于告诉浏览器不要在新窗口打开博客详情页的链接
    return render_template('blog.html', blogs=[blog], hidebloglink = True, noblank = True)


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
        form.create_user() # 调用方法 create_user() 创建用户
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
        # 执行此方法刷新【最后登录时间】
        current_user.ping()
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
