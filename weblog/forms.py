from collections.abc import Sequence
from typing import Any, Mapping
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp

from .models import db, User

class RegisterForm(FlaskForm):
    '''注册表单类'''

    name = StringField('Name', validators=[DataRequired(), Length(3, 22), Regexp('^\w+$', 0, 'User name must have only letters.')])
            # Regexp 接收三个参数：正则表达式, flags, 提示信息
            # flags 又称作 “旗标”，没有的话写为 0
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
