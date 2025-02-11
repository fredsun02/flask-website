from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature


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

    confirmed = db.Column(db.Boolean, default=False) # 用于验证user是否已经通过邮箱验证，缺省值为 False



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
    
    # 当前用户类的实例的 serializer 属性值即为令牌生成器
    @property
    def serializer(self, expires_in=3600):
        """
        创建用于生成和解析 Token 的 Serializer（令牌生成器）。

        - `SECRET_KEY` 作为加密密钥，确保 Token 只能由相同密钥解密。
        - `expires_in` 指定 Token 过期时间（默认 3600 秒 = 1 小时）。
        - `dumps(data)` 生成 Token，`loads(token)` 解析 Token。
        - **如果 `SECRET_KEY` 变了，所有之前生成的 Token 都无法解析！**
        """
        return Serializer(current_app.config['SECRET_KEY'], expires_in)

    def generate_confirm_user_token(self):
        """
        生成邮箱验证 Token，包含当前用户 ID。

        - `self.serializer.dumps({'confirm_user': self.id})` 生成 Token。
        - 生成的 Token **只能用相同 `SECRET_KEY` 解密**，否则解析失败。
        - 这个 Token 可用于邮箱验证、账号激活等功能。
        """
        return self.serializer.dumps({'confirm_user': self.id})

    def confirm_user(self, token):
        """
        验证 Token 是否有效，并确认用户身份。

        - `loads(token)` 解析 Token，检查数据是否匹配当前用户 ID。
        - **如果 `SECRET_KEY` 变了，Token 解析会失败（BadSignature 异常）。**
        - **如果 Token 过期或被篡改，解析也会失败。**
        - 解析成功后，设置 `self.confirmed = True` 并更新数据库。
        """
        try:
            data = self.serializer.loads(token)  # 解析 Token
        except BadSignature:  # Token 可能被篡改或密钥不匹配
            return False

        if data.get('confirm_user') != self.id:  # 确保 Token 归属当前用户
            return False

        self.confirmed = True  # 认证成功，标记用户为已验证
        db.session.add(self)
        db.session.commit()
        return True
