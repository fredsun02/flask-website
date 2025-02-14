'''
完成注册和验证后，用户相关的视图函数
'''

from datetime import datetime
from flask import Blueprint, abort, redirect, url_for, flash, render_template
from flask import request, current_app
from flask_login import login_required, current_user, login_user
import flask_bootstrap

from ..models import User, db, Role, Blog
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
    return render_template('user/index.html', user=user, blogs=blogs)

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
        return redirect(url_for('.index', name=current_user.name))
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
    if current_user != blog.author and not current_user.is_administrator():
        abort(403)
    form = BlogForm(obj=blog)
    if form.validate_on_submit():
        form.populate_obj(blog)
        db.session.add(blog)
        db.session.commit()
        flash('博客已更新', 'success')
        return redirect(url_for('front.blog', id=blog.id))
    return render_template('user/edit_blog.html', form=form)
