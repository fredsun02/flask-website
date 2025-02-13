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
   - 用户登录时，如果账户未验证，提供按钮“重新发送验证邮件”。

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
|蓝图注册错误 | 蓝图注册错误 | 蓝图注册地点应该为 ```handlers/__init__.py``` 文件中 |
| 表单验证错误 | 表单验证错误 | 修改表单前 user 的 confirmed 属性应为 True|
