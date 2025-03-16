from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app
from itsdangerous import TimedSerializer as Serializer  # 使用 TimedSerializer
from itsdangerous import BadSignature
from datetime import datetime
from markdown import markdown
from markdown.extensions import codehilite, fenced_code
import enum
import hashlib
import bleach
from sqlalchemy import event
from bleach.css_sanitizer import CSSSanitizer

db = SQLAlchemy()

blog_tags = db.Table('blog_tags',
    db.Column('blog_id', db.Integer, db.ForeignKey('blog.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)



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

class Follow(db.Model):
    '''存储用户关注信息的**双主键**类'''
    __tablename__ = 'follows'

    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    time_stamp = db.Column(db.DateTime, default=datetime.now)

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

    # 此属性为「我关注了谁」，属性值为查询对象，里面是 Follow 类的实例
    # 参数 foreign_keys 意为查询 User.id 值等于 Follow.follower_id 的数据
    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
        # 反向查询接口 follower 定义了 Follow 实例的属性，指向关注关系中的「关注者」，对应 Follow().follower_id 属性
        # User 实例使用 followers 属性获得 Follow 实例的时候，这些 Follow 实例的 follower 属性会指向 User 实例
        # 也就是「关注者」
        backref=db.backref('follower', lazy='joined'), 
        # 这里创建了虚拟属性！
        # 虚拟属性是指在关系中不实际存储但在查询时可以方便地访问的属性。当我们访问 follow.follower 时
        # SQLAlchemy看到follower这个属性
        # 发现这是一个relationship，所以会去User模型中查找
        # 发现这是通过User模型中的relationship定义的backref创建的
        # 知道要用follow.follower_id去查询User表
        # 自动执行类似这样的SQL：
        # SELECT * FROM user WHERE id = follow.follower_id


        # lazy='joined' 模式允许立即从联结查询中加载相关对象。
        # 例如，当某个用户关注了 100 个用户
        # 调用 user.followed.all() 后会返回一个列表，其中包含 100 个 Follow 实例，每一个实例的 follower 和 followed 回引属性都指向对应的用户
        # 设定为 lazy='joined' 模式，即可在一次数据库查询中完成这些操作
        # 如果把 lazy 设为默认值 select
        # 那么首次访问 follower 和 followed 属性时才会加载对应的用户
        # 而且每个属性都需要一个单独的查询
        # 这就意味着获取全部被关注用户时需要增加 100 次额外的数据库查询操作
        cascade='all, delete-orphan', lazy='dynamic') # 设置级联行为：
        # 1. all: 所有操作都级联（包括 save-update, merge, refresh-expire, expunge, delete）
        # 2. delete-orphan: 当记录与父对象解除关联时，自动删除这条记录

    # 此属性可获得数据库中「谁关注了我」的查询结果，它是 Follow 实例的列表
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
            backref=db.backref('followed', lazy='joined'),
            cascade='all, delete-orphan', lazy='dynamic')
    

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
    
    def is_following(self, user):
        '''判断当前用户是否关注了指定用户。self是当前用户, user是目标用户'''
        return self.followed.filter_by(followed_id=user.id).first() is not None
    
    def is_followed_by(self, user):
        '''判断指定用户是否关注了当前用户。self是当前用户, user是目标用户'''
        return self.followed.filter_by(follower_id=user.id).first() is not None
    
    def follow(self, user):
        '''关注指定用户'''
        if not self.is_following(user):
            follow = Follow(follower_id=self.id, followed_id=user.id)
            db.session.add(follow)
            db.session.commit()

    def unfollow(self, user):
        '''取消关注指定用户'''
        follow = self.followed.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)
            db.session.commit()

    @property
    def followed_posts(self):
        '''获取当前用户关注的人的博客'''
        return Blog.query.join(Follow, Follow.followed_id==Blog.author_id).filter(Follow.follower_id==self.id)
        # 使用 join 连接 Follow 和 Blog 表，只需一次数据库查询
    
class Permission:
    '''权限类'''
    FOLLOW = 1 # 关注
    WRITE = 2 # 写文章
    COMMENT = 4 # 评论
    MODERATE = 8 # 管理评论
    ADMINISTER = 128 # 管理用户

class Tag(db.Model):
    '''标签类'''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    def __repr__(self):
        return '<Tag: {}>'.format(self.name)  # 返回标签的名称
    
    @classmethod
    def remove_unused(cls):
        '''删除未使用的标签'''
        unused = cls.query.filter(~cls.blogs.any()).all()
        for tag in unused:
            db.session.delete(tag)
        db.session.commit()


class Blog(db.Model):
    '''博客映射类'''

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    title = db.Column(db.String(64))
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
    
    tags = db.relationship('Tag', secondary=blog_tags, backref=db.backref('blogs',lazy='dynamic')) # 建立与 Tag 模型的关系  

    @property  #这个装饰器使得 tags_string 可以像普通属性一样被读取
    def tags_string(self):
        '''将 tags 列表转换为字符串'''
        return ', '.join([tag.name for tag in self.tags])
    
    @tags_string.setter  # 当 tags_string 被赋值时，自动调用此方法
    def tags_string(self, value):
        """从字符串设置标签"""
        if value:  # 如果有输入标签
            self.tags = []  # 清除现有标签
            # 将字符串分割成列表：'Python, Flask' -> ['Python', 'Flask']
            tag_names = [name.strip() for name in value.split(',')]
            
            # 处理每个标签名
            for tag_name in tag_names:
                if tag_name:  # 忽略空标签
                    # 查找或创建标签
                    tag = Tag.query.filter_by(name=tag_name).first()
                    if tag is None:
                        tag = Tag(name=tag_name)
                    # 添加到博客的标签列表
                    self.tags.append(tag)

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
                       'h1', 'h2', 'h3', 'p', 'img', 'div', 'span',
                       'table', 'tr', 'td', 'th', 'tbody', 'thead']
        
        # 创建 CSS 清理器，定义允许的 CSS 属性
        css_sanitizer = CSSSanitizer(
            allowed_css_properties=['color', 'text-align']
        )

        # 处理流程：Markdown → HTML → 清洗 HTML → 处理链接 → 存储
        html = markdown(value, 
                       extensions=['fenced_code',  # 支持 ``` 代码块语法
                                 'tables',         # 支持表格
                                 'nl2br'],         # 支持换行
                       extension_configs={
                           'markdown.extensions.fenced_code': {
                               'lang_prefix': 'language-'  # 保留语言标识前缀,便于 highlight.js 识别
                           }
                       },
                       output_format='html5')
        
        print("Markdown 转换后的 HTML:", html)  # 添加这行来查看中间结果

        allowed_tags.extend(['pre', 'code', 'span', 'div'])


        cleaned = bleach.clean(
            html,
            tags=allowed_tags + ['pre', 'code', 'span'],
            attributes={
                '*': ['class', 'id', 'style', 'data-lang'],
                'a': ['href', 'rel', 'target'],
                'img': ['src', 'alt'],
                'pre': ['class', 'data-lang'],  # 添加 data-lang 属性支持
                'code': ['class', 'data-lang', 'language-*','javascript', 'python', 'html', 'css'],
                'div': ['style', 'class']
            },
            css_sanitizer=css_sanitizer  # 使用 CSS 清理器
        )
        
        # 处理链接并存储
        target.body_html = bleach.linkify(cleaned)

# 设置 SQLAlchemy 事件监听器
event.listen(Blog.body, 'set', Blog.on_changed_body)

class Comment(db.Model):
    '''评论类'''
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    time_stamp = db.Column(db.DateTime, index=True, default=datetime.now)
    disable = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')) # 当父表（User）中的记录被删除时，级联删除子表（Comment）中的记录
    author = db.relationship('User', backref=db.backref('comments', lazy='dynamic', cascade='all, delete-orphan')) # 建立与 User 模型的关系，User 为父表，Comment 为子表，设置为延迟加载，级联为删除，且当评论与用户解除关系时，自动删除评论
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id', ondelete='CASCADE')) # 当父表（Blog）中的记录被删除时，级联删除子表（Comment）中的记录
    blog = db.relationship('Blog', backref=db.backref('comments', lazy='dynamic', cascade='all, delete-orphan')) # 建立与 Blog 模型的关系，Blog 为父表，Comment 为子表，设置为延迟加载，级联为删除，且当评论与博客解除关系时，自动删除评论

