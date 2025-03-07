from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app
from itsdangerous import TimedSerializer as Serializer  # 使用 TimedSerializer
from itsdangerous import BadSignature
from datetime import datetime
from markdown import markdown
import enum
import hashlib
import bleach

db = SQLAlchemy()


class Gender(enum.Enum):
    '''性别类, Role 类 gender 属性要用到此类'''
    MALE = '男'
    FEMALE = '女'
    OTHER = '其他'


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    @staticmethod
    def insert_roles():
        # 保留所有角色初始化的代码
        # 这个方法里的代码只有在调用时才执行
        # 所以 Permission 类可以在后面定义
        roles = {
            'User': Permission.FOLLOW | Permission.COMMENT | Permission.WRITE,
            'Moderator': Permission.FOLLOW | Permission.COMMENT | Permission.WRITE | Permission.MODERATE,
            'Administrator': Permission.FOLLOW | Permission.COMMENT | Permission.WRITE | Permission.MODERATE | Permission.ADMINISTER
        }
        default_role = 'User'
        for r, v in roles.items():
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = v
            role.default = True if role.name == default_role else False
            db.session.add(role)
        db.session.commit()
        print('已初始化角色')

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
    age = db.Column(db.Integer, unique=False, index=True)  # 用户年龄，并建立索引
    gender = db.Column(db.Enum(Gender))     # 这行在类定义时就会执行，所以 Gender 类必须提前定义
    phone_number = db.Column(db.String(11), unique=True, index=True)
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text)
    
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))  # 外键，关联角色表
    role = db.relationship('Role', backref=db.backref('users', lazy='dynamic'))  # 定义用户和角色的关系

    avatar_hash = db.Column(db.String(256))  # 头像哈希值

    created_at = db.Column(db.DateTime, default=datetime.now)  # 创建时间

    last_seen = db.Column(db.DateTime, default=datetime.now)  # 最后登录时间

    confirmed = db.Column(db.Boolean, default=False) # 用于验证user是否已经通过邮箱验证，缺省值为 False


    def __init__(self, **kw):
        '''初始化实例，给用户增加默认角色'''
        # 调用父类的初始化方法
        super().__init__(**kw)
        # 然后给实例的 role 属性赋值
        self.role = Role.query.filter_by(default=True).first()

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
    def serializer(self):
        """
        创建用于生成和解析 Token 的 Serializer（令牌生成器）。

        - `SECRET_KEY` 作为加密密钥，确保 Token 只能由相同密钥解密。
        - `dumps(data)` 生成 Token，`loads(token)` 解析 Token。
        - **如果 `SECRET_KEY` 变了，所有之前生成的 Token 都无法解析！**
        """
        return Serializer(secret_key=current_app.config['SECRET_KEY'])

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

    @property
    def is_administrator(self):
        '''判断用户是否是管理员'''
        result = self.role.permissions & Permission.ADMINISTER
        if result:
            print(f"用户 {self.name} 有管理员权限 (权限值: {result})")
        else:
            print(f"用户 {self.name} 没有管理员权限 (权限值: {result})")
        return result
    
    @property
    def is_moderator(self):
        '''判断用户是否是协管员'''
        result = self.role.permissions & Permission.MODERATE
        print(f"用户 {self.name}:")
        print(f"- 当前角色: {self.role.name}")
        print(f"- 协管员权限: {'是' if result else '否'} (权限值: {result})")
        return result
    
    def has_permission(self, permission):
        '''判断用户是否有指定权限'''
        result = self.role.permissions & permission
        permission_name = {
            Permission.FOLLOW: "关注",
            Permission.COMMENT: "评论",
            Permission.WRITE: "写作",
            Permission.MODERATE: "管理",
            Permission.ADMINISTER: "超级管理"
        }.get(permission, "未知权限")
        
        print(f"用户 {self.name}:")
        print(f"- 当前角色: {self.role.name}")
        print(f"- 检查权限: {permission_name}")
        print(f"- 是否拥有: {'是' if result else '否'} (权限值: {result})")
        return result

    def ping(self):
        '''用户登录时，自动执行此方法刷新操作时间'''
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def gravatar(self, size=256, default='identicon', rating='g'):
        '''创建一个 Gravatar URL 方法，返回值为头像图片的地址'''
        # 参数：
        # size: 头像大小，默认256px
        # default: 默认头像，默认值为 'identicon'
        # rating: 头像评级，默认值为 'g'
        url = 'https://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode()).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default, rating=rating)

class Permission:
    '''权限类'''
    FOLLOW = 1 # 关注
    WRITE = 2 # 写文章
    COMMENT = 4 # 评论
    MODERATE = 8 # 管理评论
    ADMINISTER = 128 # 管理用户

class Blog(db.Model):
    '''博客映射类'''

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    time_stamp = db.Column(db.DateTime, index=True, default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))  # 当用户被删除时，删除该用户发表的博客
    # 建立与 User 模型的关系
    author = db.relationship('User', 
                           backref=db.backref('blogs', 
                                            lazy='dynamic',
                                            cascade='all, delete-orphan'))
    # 建立与 User 模型的关系
    # relationship() 提供了访问关联对象的方式，而不是直接使用外键
    # backref 会在 User 模型中添加 blogs 属性，方便反向查询
    # lazy='dynamic' 使得查询延迟执行，返回查询对象而不是结果列表
    # cascade='all, delete-orphan' 设置级联行为：
    #   - all: 所有操作都级联（包括 save-update, merge, refresh-expire, expunge, delete）
    #   - delete-orphan: 当记录与父对象解除关联时，自动删除这条记录
    author = db.relationship('User', 
                           backref=db.backref('blogs', 
                                            lazy='dynamic',
                                            cascade='all, delete-orphan'))    
    

    # 该方法为静态方法，可以写在类外部，Blog().body 有变化时自动运行
    # target 为 Blog 类的实例，value 为实例的 body 属性值
    # old_value 为数据库中 Blog.body_html 的值，initiator 是一个事件对象
    # 后两个参数为事件监听程序调用此函数时固定要传入的值，在函数内部用不到
    @staticmethod
    def on_changed_body(target, value, old_value, initiator):
        '''当 Blog.body 发生变化时自动调用此方法，将 Markdown 文本转换为安全的 HTML
        
        参数说明：
        - target: Blog 类的实例
        - value: 实例的 body 属性的新值（Markdown 文本）
        - old_value: 数据库中原有的 body_html 值
        - initiator: 事件对象（此处未使用）
        '''
        # 定义允许的 HTML 标签列表
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                       'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                       'h1', 'h2', 'h3', 'p']
        
        # 处理流程：Markdown → HTML → 清洗 HTML → 处理链接 → 存储
        target.body_html = bleach.linkify(  # 步骤3：将纯文本 URL 转换为可点击的链接
            bleach.clean(  # 步骤2：清洗 HTML，删除不安全的标签
                markdown(value, output_format='html'),  # 步骤1：将 Markdown 转换为 HTML
                tags=allowed_tags,  # 只保留允许的 HTML 标签
                strip=True  # 删除不在允许列表中的标签
            )
        )

        # 示例转换过程：
        # 1. 用户输入(Markdown)：
        #    **Hello** https://example.com
        # 2. 转换为HTML：
        #    <strong>Hello</strong> https://example.com
        # 3. 清洗HTML（保留安全标签）：
        #    <strong>Hello</strong> https://example.com
        # 4. 处理链接：
        #    <strong>Hello</strong> <a href="https://example.com">https://example.com</a>


# 设置 SQLAlchemy 事件监听器：
# 当 Blog.body 的值发生变化时，自动调用 on_changed_body 方法
# 这样用户不需要手动调用转换函数，系统会自动处理格式转换
db.event.listen(Blog.body, 'set', Blog.on_changed_body)