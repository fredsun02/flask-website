from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app

db = SQLAlchemy()


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    def __repr__(self):
        return '<Role: {}>'.format(self.name)

class User(db.Model, UserMixin):
    """
    用户模型，包含基本信息和密码加密存储功能
    """
    id = db.Column(db.Integer, primary_key=True)  # 用户ID，主键
    name = db.Column(db.String(64), unique=True, index=True)  # 用户名，唯一，并建立索引
    email = db.Column(db.String(64), unique=True, index=True)  # 用户邮箱，唯一，并建立索引
    _password = db.Column('password', db.String(256))  # 存储哈希后的密码（数据库中列名为 'password'）
    
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))  # 外键，关联角色表
    role = db.relationship('Role', backref=db.backref('users', lazy='dynamic'))  # 定义用户和角色的关系

    @property
    def password(self):
        """
        只读属性，禁止直接访问密码字段
        例如: print(user.password) 会返回哈希密码，但不能修改
        """
        return self._password

    @password.setter
    def password(self, pwd):
        """
        设置密码时自动进行哈希加密
        例如:
            user = User(name="Alice")
            user.password = "my_secure_password"  # 这里会自动哈希密码
        存入数据库的 `_password` 是加密后的值，而非明文密码
        """
        self._password = generate_password_hash(pwd)

    def verify_password(self, pwd):
        """
        验证用户密码是否正确
        例如：
            user = User(name="Alice")
            user.password = "my_secure_password"
            user.verify_password("my_secure_password")  # 返回 True
            user.verify_password("wrong_password")  # 返回 False
        """
        return check_password_hash(self._password, pwd)

    def __repr__(self):
        """
        返回用户对象的字符串表示，方便调试
        例如：
            user = User(name="Alice")
            print(user)  # 输出：<User: Alice>
        """
        return '<User: {}>'.format(self.name)