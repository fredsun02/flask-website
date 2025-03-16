from flask import Blueprint, url_for, redirect, flash, abort, request
from flask import render_template, current_app, make_response
from flask_login import login_required, login_user, logout_user, current_user
from datetime import datetime
import hashlib

from ..forms import RegisterForm, LoginForm, BlogForm, CommentForm
from ..models import db, User, Blog, Comment, Permission, Tag
from ..email import send_email
from ..decorators import moderate_required


front = Blueprint('front', __name__) # front.py - 主页相关

# 添加 Gravatar 过滤器
@front.app_template_filter('gravatar')
def gravatar_filter(email):
    """
    Jinja2 模板过滤器：将邮箱转换为 Gravatar 头像的 MD5 哈希值
    
    工作原理：
    1. 在模板中使用 {{ email | gravatar }} 时会自动调用此函数
    2. 函数接收邮箱字符串，返回其 MD5 哈希值
    3. Gravatar 使用这个哈希值作为头像的唯一标识
    
    使用示例：
    在模板中：{{ 'example@email.com' | gravatar }}
    输出示例：d4c74594d841139328695756648b6bd6
    
    最终在 img 标签中生成的 URL 示例：
    https://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6?s=200
    
    Args:
        email (str): 用户邮箱地址
        
    Returns:
        str: 邮箱的 MD5 哈希值
    """
    return hashlib.md5(email.encode()).hexdigest()




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

    # 获取所有标签
    tags = Tag.query.order_by(Tag.name).all()
    # 将分页对象和博客列表传递给模板
    return render_template('index.html', 
                         form=form,  # 发博客的表单
                         blogs=blogs,  # 当前页的博客列表
                         pagination=pagination, # 分页对象，用于生成分页导航
                         date_time=date_time, 
                         tags=tags)

@front.route('/blog/<int:id>', methods=['GET', 'POST'])
def blog(id):
    '''博客详情页'''
    blog = Blog.query.get_or_404(id)
    # hidebloglink 为布尔值，用于隐藏博客详情页的链接
    # noblank 为布尔值，用于告诉浏览器不要在新窗口打开博客详情页的链接
    # 页面提供评论输入框
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          blog=blog,
                          author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('评论发表成功', 'success')
        return redirect(url_for('.blog', id=blog.id))
    page = request.args.get('page', 1, type=int)
    pagination = blog.comments.order_by(Comment.time_stamp.desc()).paginate(
        page=page,
        per_page=10, # 暂时使用固定值
        # per_page=current_app.config['COMMENTS_PER_PAGE'],
        error_out=False
    )
    comments = pagination.items
    return render_template('blog.html', blogs=[blog], hidebloglink = True, noblank = True, form=form, comments=comments, pagination=pagination, Permission=Permission, author=blog.author)


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
        form.create_user() # 调用方法 create_user() 创x建用户
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


@front.route('/comment/disable/<int:id>')
@moderate_required
def disable_comment(id):
    '''禁用评论'''
    comment = Comment.query.get_or_404(id)
    comment.disable = True
    db.session.commit()
    flash('评论已禁用', 'success')
    # 重定向回原来的页面（比如博客详情页）
    # 不存在时返回主页
    return redirect(request.headers.get('Referer') or url_for('.index'))

@front.route('/comment/enable/<int:id>')
@moderate_required
def enable_comment(id):
    '''解封评论'''
    comment = Comment.query.get_or_404(id)
    comment.disable = False
    db.session.commit()
    flash('评论已解封', 'success')
    # 重定向回原来的页面（比如博客详情页）
    return redirect(request.headers.get('Referer') or url_for('.index'))
    

@front.route('/blogs')
def blogs():
    '''博客列表'''
    page = request.args.get('page', 1, type=int)
    pagination = Blog.query.order_by(Blog.time_stamp.desc()).paginate(
        page=page,
        per_page=current_app.config['BLOGS_PER_PAGE'],
        error_out=False
    )
    blogs = pagination.items
    # 注意这里改用 blogs.html 模板
    return render_template('blog_list.html', 
                         blogs=blogs, 
                         pagination=pagination)

@front.route('/tag/<name>')
def tag(name):
    '''显示特定标签的博客'''
    tag = Tag.query.filter_by(name=name).first()
    blogs = tag.blogs.order_by(Blog.time_stamp.desc()).paginate(
        page=request.args.get('page', 1, type=int),
        per_page=10,
        error_out=False
    )
    return render_template('tag.html', tag=tag, blogs=blogs, pagination=blogs)

@front.route('/tags')
def tags():
    '''显示所有标签'''
    tags = Tag.query.order_by(Tag.name).paginate(
        page=request.args.get('page', 1, type=int),
        per_page=10,
        error_out=False
    )
    return render_template('tags.html', tags=tags, pagination=tags)

@front.route('/about')
def about():
    '''关于'''
    return render_template('about.html')