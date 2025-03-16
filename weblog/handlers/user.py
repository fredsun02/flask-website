'''
完成注册和验证后，用户相关的视图函数
'''

from datetime import datetime
from flask import Blueprint, abort, redirect, url_for, flash, render_template
from flask import request, current_app
from flask_login import login_required, current_user, login_user
import flask_bootstrap

from ..models import User, db, Role, Blog, Permission, Tag
from ..forms import ProfileForm, AdminProfileForm, ChangePasswordForm, BeforeResetPasswordForm, ResetPasswordForm, ChangeEmailForm, BlogForm
from ..decorators import admin_required
from ..email import send_email

user = Blueprint('user', __name__, url_prefix='/user') # URL 前缀，所有该蓝图的路由都会加上这个前缀

@user.route('/<name>/index')
def index(name):
    '''用户主页'''
    user = User.query.filter_by(name=name).first()
    if user is None:
        abort(404)
    blogs = user.blogs.order_by(Blog.time_stamp.desc()).all()
    return render_template('user/index.html', user=user, blogs=blogs, Permission=Permission)

@user.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    '''修改个人信息'''
    print("=== 进入 edit_profile 函数 ===")
    print(f"请求方法: {request.method}")
    print(f"表单数据: {request.form}")  # 打印表单数据
    
    form = ProfileForm(current_user, obj=current_user)
    if form.validate_on_submit():
        print("表单验证通过")
        form.populate_obj(current_user)
        db.session.add(current_user)
        db.session.commit()
        flash('个人信息已更新', 'success')
        return redirect(url_for ('.index', name=current_user.name))
    else:
        print("表单验证失败")
        print("表单错误:", form.errors)  # 打印表单错误
    
    return render_template('user/edit_profile.html', form=form)
    

@user.route('/admin-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_profile(id):
    '''管理员修改用户信息'''
    user = User.query.get(id)
    form = AdminProfileForm(user, obj=user)
    print("Hello")
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.add(user)
        db.session.commit()
        flash('用户信息已更新', 'success')
        return redirect(url_for('.index', name=user.name))
    return render_template('user/edit_profile.html', form=form)

@user.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    '''修改密码'''
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = form.password.data
        db.session.add(current_user)
        db.session.commit()
        flash('密码已更新', 'success')
        return redirect(url_for('.index', name=current_user.name))
    return render_template('user/change_password.html', form=form)


@user.route('/before-reset-password', methods=['GET', 'POST'])
def before_reset_password():
    '''重置密码前，验证邮箱'''
    form = BeforeResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        token = user.generate_confirm_user_token()
        
        # 打印调试信息
        print("\n=== 重置密码邮件信息 ===")
        print(f"用户: {user.name}")
        print(f"邮箱: {user.email}")
        print(f"令牌: {token}")
        print(f"邮件内容:")
        print(render_template('email/reset_password.txt', user=user, token=token))
        
        send_email(user, user.email, 'reset_password', token)
        flash('重置密码邮件已发送', 'success')
    return render_template('user/reset_password.html', form=form)



@user.route('/reset-password/<name>/<token>', methods=['GET', 'POST'])
def reset_password(name, token):
    '''重置密码时，点击验证邮件中的链接时，用此视图函数处理'''
    user = User.query.filter_by(name=name).first()
    if user and user.confirm_user(token):
        form = ResetPasswordForm()
        if request.method == 'GET':
            flash('邮箱已确认，请重置密码')
            return render_template('user/reset_password.html', form=form)
        if form.validate_on_submit():
            user.password = form.password.data
            db.session.add(user)
            db.session.commit()
            flash('密码已更新', 'success')
            return redirect(url_for('.index', name=user.name))
    flash('链接错误，请重试')
    return redirect(url_for('front.index'))

@user.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email():
    '''更换邮箱'''
    form = ChangeEmailForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.confirmed = 0
        db.session.add(current_user)
        db.session.commit()
        token = current_user.generate_confirm_user_token()
        send_email(current_user, current_user.email, 'change_email', token)
        flash('邮箱已更新，请验证新邮箱', 'success')
    return render_template('user/change_email.html', form=form)


@user.route('/change-email/<token>')
@login_required
def confirm_change_email(token):
    '''变更邮箱时，验证新邮箱，邮箱中的链接用此视图函数处理'''
    if current_user.confirmed(token):
        current_user.confirmed = 1
        db.session.add(current_user)
        db.session.commit()
        flash('邮箱已确认，请登录', 'success')
        return redirect(url_for('.login', name=current_user.name))
    flash('验证链接错误，请重试', 'danger')
    return redirect(url_for('front.index'))



@user.route('/edit-blog/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_blog(id):
    '''编辑博客'''
    blog = Blog.query.get_or_404(id)
    if current_user != blog.author and not current_user.is_administrator:
        abort(403)
    form = BlogForm(obj=blog)
    if form.validate_on_submit():
        form.populate_obj(blog)
        db.session.add(blog)
        db.session.commit()
        flash('博客已更新', 'success')
        return redirect(url_for('front.blog', id=blog.id))
    return render_template('user/edit_blog.html', form=form)

@user.route('/delete-blog/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_blog(id):
    '''删除博客（仅管理员）'''
    blog = Blog.query.get_or_404(id)
    
    if request.method == 'POST':  # 只在 POST 请求时执行删除操作
        try:
            db.session.delete(blog)
            Tag.remove_unused()
            db.session.commit()
            flash('博客已删除', 'success')
        except Exception as e:
            db.session.rollback()
            flash('删除失败', 'danger')
    
    return redirect(url_for('front.blogs'))


@user.route('/follow/<name>')
@login_required
def follow(name):
    '''关注指定用户'''
    user = User.query.filter_by(name=name).first()
    if not user:
        flash('用户不存在', 'warning')
        return redirect(url_for('front.index'))
    if current_user.is_following(user):
        flash('已关注', 'info')
    else:
        current_user.follow(user)
        flash('关注成功！', 'success')
    return redirect(url_for('.index', name=name))

@user.route('/unfollow/<name>')
@login_required
def unfollow(name):
    '''取关指定用户'''
    user = User.query.filter_by(name=name).first()
    if not user:
        flash('用户不存在', 'warning')
        return redirect(url_for('front.index'))
    if not current_user.is_following(user):
        flash('用户未关注！', 'info')
    else:
        current_user.unfollow(user)
        flash('取消关注成功！', 'success')
    return redirect(url_for('.index', name=name))

@user.route('<name>/followed')
def followed(name):
    '''显示user关注的用户列表'''
    user = User.query.filter_by(name=name).first()
    if not user:
        flash('用户不存在', 'warning')
        return redirect(url_for('front.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page=page,
        # per_page=current_app.config['USERS_PER_PAGE'],
        per_page=10, # 暂时使用固定值
        error_out=False
    )

    follows = []
    for follow in pagination.items:
        follow_dict = {
            'user': follow.followed,      # 被关注的用户对象
            'time_stamp': follow.time_stamp  # 关注的时间
        }
        follows.append(follow_dict)

    return render_template('user/follow.html', user=user, title="我关注的人",
                           endpoint='user.followed', pagination=pagination,
                           follows=follows)

@user.route('<name>/followers')
def followers(name):
    '''显示user的粉丝列表'''
    user = User.query.filter_by(name=name).first()
    if not user:
        flash('用户不存在', 'warning')
        return redirect(url_for('front.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page=page,
        # per_page=current_app.config['USERS_PER_PAGE'],
        per_page=10, # 暂时使用固定值
        error_out=False
    )
    follows = []
    for follow in pagination.items:
        follow_dict = {
            'user': follow.follower,
            'time_stamp': follow.time_stamp
        }
        follows.append(follow_dict)
    return render_template('user/follow.html', user=user, title="我的粉丝",
                           endpoint='user.followers', pagination=pagination,
                           follows=follows)

@user.route('/<name>/write_blog', methods=['GET', 'POST'])
@login_required
def write_blog(name):
    '''发表博客'''
    form = BlogForm()
    if form.validate_on_submit():
        blog = Blog()
        form.populate_obj(blog)
       
        blog.author = current_user
        db.session.add(blog)
        db.session.commit()

        flash('发表成功', 'success')
        return redirect(url_for('.index', name=current_user.name))
    return render_template('user/write_blog.html', form=form)

