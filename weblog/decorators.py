from functools import wraps
from flask import abort, flash, render_template, redirect, url_for
from flask_login import current_user
from datetime import datetime


from .models import Permission, Blog
from .handlers import front



def permission_required(permission):
    '''权限检查装饰器工厂函数
    
    当使用 @permission_required(Permission.XXX) 装饰一个函数时：
    1. permission_required(Permission.XXX) 被调用，返回 decorator 函数
    2. decorator(原始函数) 被调用，返回 decorated_func 函数
    3. 原始函数被 decorated_func 替换
    4. 当之后调用这个函数时，实际上是在调用 decorated_func
       - 它会先检查权限
       - 有权限就调用原始函数
       - 没权限就重定向到首页
    '''

    def decorator(func):
        '''真正的装饰器函数，接收被装饰的原始函数'''
        @wraps(func)  # 保留原始函数的元数据（如函数名、文档字符串等）
        def decorated_func(*args, **kwargs):
            '''包装后的函数，先检查权限再决定是否执行原始函数'''
            # 检查用户是否有指定权限
            if not current_user.role.permissions & permission:
                flash('你这个号权限太低啦', 'warning')
                return redirect(url_for('front.index'))
            # 有权限就执行原始函数
            return func(*args, **kwargs)
        return decorated_func
    return decorator

admin_required = permission_required(Permission.ADMINISTER)
moderate_required = permission_required(Permission.MODERATE)