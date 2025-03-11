### 开发日志 - 11.02.25

#### 今日开发内容
今天的主要任务是为 Flask 项目添加邮箱验证功能，用户在注册账户后，系统会自动发送验证邮件，用户点击邮件中的链接后，即可完成账户验证。

#### 实现功能
1. **注册用户后发送邮箱验证邮件**
   - 用户在 `/register` 注册后，系统会使用 `Flask-Mail` 发送验证邮件。
   - 生成令牌 (`token`)，并将其附加到验证链接中。
   - 用户点击邮件中的链接后，`/confirm-user/<token>` 端点会校验 `token`，验证通过则激活账户。

2. **令牌 (`token`) 机制**
   - 采用 `itsdangerous.Serializer` 进行令牌加密，防止篡改。
   - `token` 包含用户 ID，并设置过期时间（如 1 小时）。
   - 通过 `confirm_user(token)` 方法进行验证。

3. **邮件模板**
   - 使用 Jinja2 模板引擎创建 HTML + 纯文本邮件模板（存放在 `templates/email`）。
   - 确保邮件正文支持 HTML 和 纯文本（适配不同客户端）。

4. **用户未验证时限制部分操作**
   - 未验证用户只能进行有限操作，如不能创建内容。
   - 访问受限页面时，会被重定向到 `/unconfirmed_user` 页面，并提示用户需要完成邮箱验证。

#### 关键技术 & 原理
1. **Flask-Mail 发送邮件**
   - 通过 SMTP 服务器发送邮件（Gmail、QQ、Outlook 等）。
   - 采用多线程处理邮件发送，以避免影响主进程响应请求。
   
   ```python
   def send_async_email(app, msg):
       with app.app_context():
           Mail(app).send(msg)
   ```

2. **itsdangerous 令牌管理**
   - 令牌 (`token`) 采用 `SECRET_KEY` 进行加密。
   - `generate_confirm_user_token()` 生成令牌。
   - `confirm_user(token)` 解析令牌并验证用户身份。
   
   ```python
   def generate_confirm_user_token(self):
       return self.serializer.dumps({'confirm_user': self.id})
   ```

3. **邮件模板**
   - HTML 模板 (`confirm_user.html`)
   - 纯文本模板 (`confirm_user.txt`)
   - 通过 `render_template()` 生成邮件内容。
   
   ```html
   <a href="{{ url_for('front.confirm_user', token=token, _external=True) }}">点击这里验证邮箱</a>
   ```

#### 遇到的 Bug & 解决方案
| **问题** | **原因** | **解决方案** |
|----------|---------|-------------|
| `KeyError: 'mail'` | `Mail(app)` 没有初始化 | 在 `app.py` 的 `register_extensions(app)` 里初始化 `Mail(app)` |
| `SMTP Authentication Required` | 没有启用 Gmail **应用专用密码** | 生成 Gmail **专用密码**，或改用 QQ/Outlook 邮箱 |
| `ModuleNotFoundError: No module named 'email_validator'` | 缺少 `email_validator` 依赖 | `pip install email_validator` 重新安装 |

#### 未解决问题
1. **SMTP 服务器登录失败**
   - 仍然无法成功通过 SMTP 发送邮件，Gmail、QQ 和 Outlook 账号均遇到认证问题：
     - Gmail: "5.7.0 Authentication Required"
     - QQ: "Error: need EHLO and AUTH first"
   - 计划尝试：
     - 检查 Gmail 应用专用密码
     - 确保 QQ SMTP 配置正确
     - 测试 Mailtrap 进行调试

2. **完善用户体验**
   - 添加更换邮箱功能。
   - 用户登录时，如果账户未验证，提供按钮"重新发送验证邮件"。

#### 总结
今天的开发任务主要围绕用户邮箱验证进行，成功实现了用户注册后发送验证邮件的功能，并且利用 `itsdangerous` 进行 `token` 令牌管理。尽管仍然面临 SMTP 认证失败的问题，但已确定了进一步排查方案。


### 开发日志 - 12.02.25

#### 今日开发内容
今天的主要任务是完善用户权限管理系统，包括角色权限的初始化、权限检查功能的优化，以及添加了更直观的权限检查输出信息。

#### 实现功能
1. **角色权限系统的完善**
   - 实现了角色的自动初始化功能
   - 完善了权限检查机制
   - 添加了详细的权限检查输出信息

2. **权限检查方法的优化**
   - 改进了 `is_administrator` 属性
   - 改进了 `is_moderator` 属性
   - 优化了 `has_permission` 方法
   - 添加了详细的权限信息输出

3. **权限系统的可视化输出**
   - 添加了用户角色信息的打印
   - 显示具体的权限值
   - 提供了权限检查的详细结果

#### 关键技术 & 原理
1. **位运算权限管理**
   ```python
   class Permission:
       FOLLOW = 1      # 00000001
       COMMENT = 2     # 00000010
       WRITE = 4       # 00000100
       MODERATE = 8    # 00001000
       ADMINISTER = 128 # 10000000
   ```

2. **权限检查方法**
   ```python
   @property
   def is_administrator(self):
       result = self.role.permissions & Permission.ADMINISTER
       print(f"用户 {self.name}:")
       print(f"- 当前角色: {self.role.name}")
       print(f"- 管理员权限: {'是' if result else '否'} (权限值: {result})")
       return result
   ```

3. **通用权限检查**
   ```python
   def has_permission(self, permission):
       result = self.role.permissions & permission
       permission_name = {
           Permission.FOLLOW: "关注",
           Permission.COMMENT: "评论",
           Permission.WRITE: "写作",
           Permission.MODERATE: "管理",
           Permission.ADMINISTER: "超级管理"
       }.get(permission, "未知权限")
       # ... 输出详细信息 ...
       return result
   ```

#### 遇到的 Bug & 解决方案
| **问题** | **原因** | **解决方案** |
|----------|---------|-------------|
| `TimedJSONWebSignatureSerializer` 导入错误 | itsdangerous 版本兼容性问题 | 改用 `URLSafeSerializer` |
| 权限值显示不直观 | 缺少详细输出信息 | 添加了格式化的权限信息打印 |

#### 未解决问题
**expires_in 参数被移除**

#### 总结
今天主要完成了用户权限系统的优化工作，通过添加详细的权限检查输出信息，使系统的权限管理更加直观和易于调试。虽然遇到了一些拼写错误和版本兼容性的问题，但都得到了及时解决。后续还需要继续完善权限管理的用户界面，提升整体用户体验。


### 开发日志 - 13.02.25

#### 今日开发内容
今天的开发任务是实现用户个人主页的渲染，包括用户和管理员编辑信息的功能，以及相应的视图函数、表单类和前端模板。

#### 实现功能
1. **完善 User 映射类**
   - 添加了 `age`, `gender`, `phone_number`, `location`, `about_me` 属性
   - 其中 `gender` 是枚举类型的数据，定义了一个特别的 Gender 类，继承自 enum.Enum 类
2. **展示用户最近活动时间**
   - 在主页模板中添加了用户最近活动时间的展示
   - 定义了一个新方法 ping()，每次登录时 @front.before_app_request 装饰器会调用它
   - 该方法会更新用户的 last_seen 属性 ```self.last_seen = datetime.utcnow()```
3. **创建了 User 蓝图**
   - 实现了用户主页的展示功能，用户可以通过 `/user/<name>/index` 路由访问自己的主页。
   - 提供了用户编辑个人信息的功能，用户可以通过 `/user/edit-profile` 路由修改自己的信息。
   - 实现了管理员编辑用户信息的功能，管理员可以通过 `/user/admin-profile/<int:id>` 路由修改任意用户的信息。
   - 使用了权限控制，确保只有登录用户才能访问编辑功能，并且只有管理员才能访问管理员编辑功能。
4. **创建了 ProfileForm 和 AdminProfileForm 表单类**
   - 继承自 Flask-WTF 的 Form 类
   - 定义了用户和管理员编辑信息的表单
   - 表单类中定义了性别选择框，使用 Flask-Bootstrap 的 Form.RadioItem 类来生成单选按钮
   - 定义了新方法 validate_name() 和 validate_phone_number() 来验证用户名和手机号是否已存在
5. **创建了 decorators.py 文件**
   - 定义了 admin_required 装饰器，用于检查用户是否具有管理员权限
   - 定义了 permission_required 装饰器，用于检查用户是否具有特定权限

#### 遇到的 Bug & 解决方案
| **问题** | **原因** | **解决方案** |
|----------|---------|-------------|
| `AttributeError: 'User' object has no attribute 'role'` | 缺少 role 属性 | 修改权限检查逻辑为 ```self.role.permissions & permission``` 而非 ```self.role(permission) == permission``` |
| 蓝图注册错误 | 蓝图注册错误 | 蓝图注册地点应该为 ```handlers/__init__.py``` 文件中 |
| 表单验证错误 | 表单验证错误 | 修改表单前 user 的 confirmed 属性应为 True|

### 开发日志 - 14.02.25

#### 今日开发内容
今天的主要任务是实现用户头像功能，包括添加 Gravatar 头像支持、注册流程集成和用户界面展示。

#### 实现功能
1. **添加 Gravatar 头像支持**
   - 在 User 模型中添加 `avatar_hash` 字段，用于存储头像 URL
   - 实现 `gravatar()` 方法，生成基于邮箱的默认头像
   ```python
   def gravatar(self, size=256, default='identicon', rating='g'):
       url = 'https://www.gravatar.com/avatar'
       hash = self.avatar_hash or hashlib.md5(self.email.encode()).hexdigest()
       return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
           url=url, hash=hash, size=size, default=default, rating=rating)
   ```
   - 默认使用 identicon 风格，生成独特的几何图案作为头像
   - 支持自定义头像大小、默认样式和评级

2. **注册流程集成**
   - 在用户注册时自动生成并保存头像 URL
   ```python
   def create_user(self):
       user = User()
       self.populate_obj(user)
       user.avatar_hash = user.gravatar()  # 生成并保存头像URL
       db.session.add(user)
       db.session.commit()
   ```

3. **用户界面展示**
   - 在用户主页添加头像显示
   ```html
   <div class="col-md-3">
       <img class="img-rounded profile-thumbnail"
            src="{% if user.avatar_hash %}
                   {{ user.avatar_hash }}
                 {% else %}
                   {{ user.gravatar(size=256) }}
                 {% endif %}" />
   </div>
   ```
   - 支持头像回退机制：如果 `avatar_hash` 为空，则实时生成头像

#### 技术细节
- 使用 Gravatar 服务作为头像提供方
- 通过 MD5 哈希用户邮箱来生成唯一的头像标识
- 支持的参数：
  - size: 头像大小（默认 256px）
  - default: 默认头像样式（使用 identicon）
  - rating: 内容分级（使用 G 级）

#### 遇到的 Bug & 解决方案
| **问题** | **原因** | **解决方案** |
|----------|---------|-------------|
| 数据库字段错误 | 模型类和数据库表字段名不一致 | 统一使用 `create_at` 作为字段名 |
| 角色分配失败 | 数据库中没有初始化角色数据 | 需要先调用 `Role.insert_roles()` 初始化角色 |


### 开发日志 II - 14.02.25

#### 今日开发内容
今天主要完成了用户账户管理的核心功能，包括密码修改、忘记密码时的重置功能，以及邮箱更换功能。重点是通过邮件验证来确保这些敏感操作的安全性。

#### 实现功能
1. **密码管理功能**
   - 已登录用户修改密码（需验证旧密码）
   - 忘记密码时通过邮箱重置
   - 重置密码时的邮件验证机制

2. **邮箱验证系统**
   - 复用已有的令牌验证机制
   - 统一的邮件发送流程
   - HTML/纯文本双格式邮件模板

#### 关键技术 & 原理
1. **表单验证机制**
   ```python
   class ChangePasswordForm(FlaskForm):
       old_password = PasswordField('旧密码', validators=[DataRequired()])
       password = PasswordField('新密码', validators=[
           DataRequired(), 
           Length(3, 22), 
           NotEqualTo('old_password', message='新密码不能与旧密码相同')
       ])
   ```

2. **令牌验证复用**
   - 复用 `generate_confirm_user_token()` 生成重置密码令牌
   - 复用 `confirm_user()` 验证令牌有效性
   - 统一的安全验证机制

3. **视图函数的双重请求处理**
   ```python
   @user.route('/reset-password/<name>/<token>', methods=['GET', 'POST'])
   def reset_password(name, token):
       # 先验证用户身份和令牌
       if user and user.confirm_user(token):
           form = ResetPasswordForm()
           # GET 请求：显示表单页面
           if request.method == 'GET':
               return render_template('template.html', form=form)
           # POST 请求：处理表单提交
           if form.validate_on_submit():
               # 更新数据库
               return redirect(url_for('success_page'))
   ```

#### 遇到的 Bug & 解决方案
1. **重置密码链接无效**
   - 问题：使用了错误的令牌验证方法名
   - 解决：将 `confirm_user_token` 改为 `confirm_user`

2. **邮件模板语法错误**
   - 问题：URL 生成函数中多余的单引号
   - 解决：修正模板中的语法错误

#### 安全性考虑
1. 所有密码相关操作都需要邮件验证
2. 重置密码链接具有时效性
3. 令牌包含用户ID，确保操作针对特定用户


### 开发日志 III - 14.02.25

#### 今日开发内容
今天主要完成了博客系统的核心功能开发，包括博客的发布、展示、编辑功能，以及分页显示和 Markdown 支持。

#### 实现功能
1. **博客数据模型**
   - 创建 Blog 表，包含博客内容、HTML 内容、时间戳等字段
   - 实现与 User 表的一对多关联
   ```
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
   ```

2. **博客发布功能**
   - 实现博客发布表单
   - 支持 Markdown 编辑和预览
   - 自动转换 Markdown 为 HTML
   ```
   class BlogForm(FlaskForm):
      '''博客表单类'''

      # 这里使用 Flask-PageDown 提供的字段类，以支持 Markdown 编辑
      # 前端再设置一下预览，就可以在输入框输入 Markdown 语句并显示在页面上
      body = PageDownField('博客内容', validators=[DataRequired()])
      submit = SubmitField('提交')
   ```

3. **博客展示系统**
   - 创建博客列表模板
   - 实现分页功能
   - 支持时间本地化显示
   ```
   weblog/templates/_blogs.html
   ```

4. **博客编辑功能**
   - 作者编辑权限控制
   - 管理员编辑权限
   - Markdown 实时预览
   ```
   @user.route('/edit-blog/<int:id>', methods=['GET', 'POST'])
   @login_required
   def edit_blog(id):
      '''编辑博客'''
      blog = Blog.query.get_or_404(id)
      if current_user != blog.author and not current_user.is_administrator():
         abort(403)
      form = BlogForm(obj=blog)
      if form.validate_on_submit():
         form.populate_obj(blog)
         db.session.add(blog)
         db.session.commit()
         flash('博客已更新', 'success')
         return redirect(url_for('front.blog', id=blog.id))
      return render_template('user/edit_blog.html', form=form)
   ```

#### 关键技术 & 原理
1. **分页查询实现**
   ```python
   pagination = Blog.query.order_by(Blog.time_stamp.desc()).paginate(
       page=page,
       per_page=current_app.config['BLOGS_PER_PAGE'],
       error_out=False
   )
   ```

2. **Markdown 支持**
   - 使用 Flask-PageDown 提供编辑器界面
   - 使用 Markdown 库进行格式转换
   - 使用 Bleach 清理 HTML，防止 XSS 攻击

3. **权限控制**
   ```python
   if current_user != blog.author and not current_user.is_administrator:
       abort(403)
   ```

#### 遇到的 Bug & 解决方案
| **问题** | **原因** | **解决方案** |
|----------|---------|-------------|
| 编辑链接格式错误 | URL 生成模板中多余空格 | 修正模板语法，移除多余空格 |
| 头像大小不一致 | CSS 样式未统一 | 统一设置头像大小为 32px |

#### 待优化项目
1. 添加博客评论功能
2. 实现博客分类和标签
3. 添加博客搜索功能
4. 优化编辑器界面
5. 实现图片上传功能

#### 环境依赖
- Flask-PageDown
- Markdown
- Bleach

### 开发日志 15.02.25

修改 decorator 装饰器，从原本 abort(403) 改为 return redirect(url_for('front.index'))，同时 flash('你这个号权限太低啦', 'warning')

### 开发日志 - 11.03.25

#### 今日开发内容
今天主要实现了用户关注系统的功能，包括关注/取消关注用户、显示关注状态以及关注列表的展示。

#### 实现功能
1. **用户关注功能**
   - 实现了用户关注和取消关注功能
   - 添加了关注状态显示（互相关注、已关注等）
   - 实现了性别相关的代词显示（他/她/TA）

2. **关注列表展示**
   - 实现了用户关注列表的展示
   - 实现了用户粉丝列表的展示
   - 添加了分页功能
   ```python
   @user.route('<name>/followed')
   def followed(name):
       '''显示user关注的用户列表'''
       user = User.query.filter_by(name=name).first()
       if not user:
           flash('用户不存在', 'warning')
           return redirect(url_for('front.index'))
       page = request.args.get('page', 1, type=int)
       pagination = user.followed.paginate(
           page=page,
           per_page=10,
           error_out=False
       )
       follows = []
       for follow in pagination.items:
           follow_dict = {
               'user': follow.followed,      # 被关注的用户对象
               'time_stamp': follow.time_stamp  # 关注的时间
           }
           follows.append(follow_dict)
       return render_template('user/follow.html', 
                            user=user, 
                            title="我关注的人",
                            endpoint='user.followed', 
                            pagination=pagination,
                            follows=follows)
   ```

3. **权限控制**
   - 添加了关注功能的权限检查
   - 只有登录用户才能看到关注按钮
   - 用户不能关注自己

#### 关键技术 & 原理
1. **关注关系处理**
   - 使用中间表存储关注关系
   - 通过 SQLAlchemy 的 relationship 实现多对多关系
   - 记录关注时间戳

2. **状态判断方法**
   - `is_following()` 判断是否已关注
   - `is_followed_by()` 判断是否被关注
   - 结合两个方法判断是否互相关注

#### 遇到的 Bug & 解决方案
| **问题** | **原因** | **解决方案** |
|----------|---------|-------------|
| 分页参数错误 | 配置项未正确加载 | 临时使用固定值10作为每页显示数量 |
| 权限检查报错 | 错误的方法调用方式 | 修正权限检查的调用方式 |
| 模板渲染错误 | 条件判断顺序问题 | 调整模板中条件判断的顺序 |



