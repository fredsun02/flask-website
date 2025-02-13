from collections.abc import Sequence
from typing import Any, Mapping
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, IntegerField, RadioField, TextAreaField, SelectField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp

from .models import db, User, Role

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
        