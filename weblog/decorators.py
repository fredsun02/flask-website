from functools import wraps
from flask import abort, flash, render_template, redirect, url_for
from flask_login import current_user
from datetime import datetime


from .models import Permission, Blog
from .handlers import front



def permission_required(permission):
    '''嵌套装饰器函数，返回值为各种装饰器'''

    def decorator(func):
        @wraps(func)
        def decorated_func(*args, **kwargs):
            if not current_user.role.permissions & permission:
                flash('你这个号权限太低啦', 'warning')
                return redirect(url_for('front.index'))
        return decorated_func
    return decorator

admin_required = permission_required(Permission.ADMINISTER)
moderate_required = permission_required(Permission.MODERATE)