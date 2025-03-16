from collections.abc import Sequence
from typing import Any, Mapping
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, IntegerField, RadioField, TextAreaField, SelectField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, Optional
from flask_login import current_user
from flask_pagedown.fields import PageDownField  # 从 fields 子模块导入

from .models import db, User, Role
from .email import send_email

class RegisterForm(FlaskForm):
    '''注册表单类'''

    name = StringField('Name', validators=[DataRequired(), Length(3, 22), Regexp('^\w+$', 0, 'User name must have only letters.')])
            # Regexp 接收三个参数：正则表达式, flags, 提示信息
            # flags 又称作 "旗标"，没有的话写为 0
    email = StringField('Email', validators=[DataRequired(), Length(3, 22)])
    password = PasswordField('Password', validators=[DataRequired(), Length(3, 22)])
    repeat_password = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
        
    def validate_name(self, field):
        if User.query.filter_by(name=field.data).first():
            raise ValidationError('Name already registered.')
        
    def create_user(self):
        '''创建新用户并存入数据库，发送验证邮件'''
        user = User()
        # 自动将表单中的所有字段数据（name、email、password等）
        # 复制到 user 对象的对应属性中
        # 相当于：
        # user.name = self.name.data
        # user.email = self.email.data
        # user.password = self.password.data
        self.populate_obj(user)
        # 添加头像路由
        user.avatar_hash = user.gravatar()
        db.session.add(user)
        db.session.commit()
        # 发送验证邮件
        # 使用令牌生成器生成 token，作为验证链接的一部分
        # 视图函数 front.confirm_user 会调用 user.confirm_user 方法
        # 该方法使用令牌生成器的 loads 验证 token
        token = user.generate_confirm_user_token()
        send_email(user, user.email, 'confirm_user', token)
        return user


class LoginForm(FlaskForm):
    '''登录表单类'''

    email = StringField('Email', validators=[DataRequired(), Length(6, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(3, 22)])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Login')

class ProfileForm(FlaskForm):
    '''用户个人信息表单类'''

    name = StringField('用户名', validators=[DataRequired(), Length(1, 22), Regexp('^\w+$', 0, '用户名必须由字母、数字和下划线组成。')])
    age = IntegerField('年龄')
    gender = RadioField('性别', choices=[('male', '男'), ('female', '女'), ('other', '其他')])
    phone_number = StringField('电话号码', validators=[Length(6, 16)])
    location = StringField('位置', validators=[Length(0, 64)])
    about_me = TextAreaField('个人简介')
    submit = SubmitField('提交')

    def validate_name(self, field):
        if (field.data != self.user.name and User.query.filter_by(name=field.data).first()):
            raise ValidationError('用户名已存在')
    
    def validate_phone_number(self, field):
        if (field.data != self.user.phone_number and User.query.filter_by(phone_number=field.data).first()):
            raise ValidationError('电话号码已存在')
        
    def __init__(self, user, *args, **kwargs):
        '''创建该类实例时，需要提供一个用户对象作为参数'''
        # 基类 FlaskForm 有 __init__ 方法，这里需要 super 方法执行基类的同名方法
        super().__init__(*args, **kwargs)
        # 需要提供被修改的用户实例作为参数，自定义表单验证器要用
        self.user = user

class AdminProfileForm(FlaskForm):
    '''管理员个人信息表单类'''

    name = StringField('用户名', validators=[DataRequired(), Length(1, 22), Regexp('^\w+$', 0, '用户名必须由字母、数字和下划线组成。')])
    age = IntegerField('年龄')
    gender = RadioField('性别', choices=[('male', '男'), ('female', '女'), ('other', '其他')])
    phone_number = StringField('电话', validators=[Length(6, 16)])
    location = StringField('所在城市', validators=[Length(2, 16)])
    about_me = TextAreaField('个人简介')
    # 这个选择框，选择的结果就是 int 数值，也就是用户的 role_id 属性值
    # 参数 coerce 规定选择结果的数据类型
    # 该选择框须定义 choices 属性，也就是选项列表
    # 每个选项是一个元组，包括 int 数值（页面不可见）和选项名（页面可见）
    # 选择某个选项，等号前面的变量 role_id 就等于对应的 int 数值
    role_id = SelectField('角色', coerce=int)
    confirmed = BooleanField('已通过邮箱验证')
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 初始化表单类实例时，需要定义好 SelectField 所需的选项列表
        self.role_id.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        

class NotEqualTo:
    """
    验证两个字段的值不相等
    """
    def __init__(self, fieldname, message=None):
        self.fieldname = fieldname
        self.message = message or '新密码不能与旧密码相同'

    def __call__(self, form, field):
        try:
            other = form[self.fieldname]
        except KeyError:
            raise ValidationError(field.gettext("Invalid field name '%s'.") % self.fieldname)
        
        if field.data == other.data:
            raise ValidationError(self.message)


class ChangePasswordForm(FlaskForm):
    '''用户登录后更换密码表单类'''
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    password = PasswordField('新密码', validators=[DataRequired(), Length(3, 22), NotEqualTo('old_password', message='新密码不能与旧密码相同')])
    repeat_password = PasswordField('重复新密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('递交')

    def validate_old_password(self, field):
        if not current_user.verify_password(self.old_password.data):
            raise ValidationError('旧密码错误')
        
class BeforeResetPasswordForm(FlaskForm):
    '''忘记密码时利用邮箱重置密码前所使用的【邮箱】表单类'''
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    submit = SubmitField('提交')

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError('未注册')
        

class ResetPasswordForm(FlaskForm):
    '''忘记密码时利用邮箱重置密码时所使用的【密码】表单类'''

    password = PasswordField('新密码', validators=[DataRequired(), Length(3, 22)])
    repeat_password = PasswordField('重复新密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('递交')



class ChangeEmailForm(FlaskForm):
    '''用户登录后更换邮箱表单类'''
    email = StringField('新邮箱', validators=[DataRequired(), Email()])
    repeat_email = StringField('重复新邮箱', validators=[DataRequired(), EqualTo('email')])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('递交')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已存在')
        
    def validate_password(self, field):
        if not current_user.verify_password(field.data):
            raise ValidationError('密码错误')

class BlogForm(FlaskForm):
    '''博客表单类'''

    # 这里使用 Flask-PageDown 提供的字段类，以支持 Markdown 编辑
    # 前端再设置一下预览，就可以在输入框输入 Markdown 语句并显示在页面上
    title = StringField('标题', validators=[DataRequired()])
    tags_string = StringField('标签（用逗号分隔）', validators=[Optional()])
    body = PageDownField('博客内容', validators=[DataRequired()])
    submit = SubmitField('提交')

class CommentForm(FlaskForm):
    '''评论表单类'''
    body = TextAreaField('评论内容', validators=[DataRequired()])
    submit = SubmitField('提交')