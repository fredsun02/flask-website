'''
完成注册和验证后，用户相关的视图函数
'''

from datetime import datetime
from flask import Blueprint, abort, redirect, url_for, flash, render_template
from flask import request, current_app
from flask_login import login_required, current_user, login_user
import flask_bootstrap

from ..models import User, db, Role
from ..forms import ProfileForm, AdminProfileForm
from ..decorators import admin_required

user = Blueprint('user', __name__, url_prefix='/user') # URL 前缀，所有该蓝图的路由都会加上这个前缀

@user.route('/<name>/index')
def index(name):
    '''用户主页'''
    user = User.query.filter_by(name=name).first()
    if user is None:
        abort(404)
    return render_template('user/index.html', user=user)

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

