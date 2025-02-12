from flask import current_app, render_template, flash
from flask_mail import Mail, Message
from threading import Thread

def send_async_email(app, msg):
    '''
    该函数作为线程类实例化时 target 参数的值，在线程中执行
    在单独的线程中发送邮件，防止 Flask 服务器因邮件发送而阻塞。

    参数：
        app (Flask): Flask 应用实例，需要手动提供应用上下文。
        msg (Message): Flask-Mail 的 Message 对象，包含邮件内容。

    运行流程：
    1. 由于 Flask 线程默认不会继承应用上下文，因此需要手动创建上下文 `with app.app_context():`。
    2. 在该上下文中实例化 Flask-Mail 并调用 `send(msg)` 发送邮件。
    3. 该函数通常不会直接调用，而是作为 `Thread(target=send_async_email, args=(app, msg))` 的目标函数，
       这样邮件发送就在一个单独的后台线程中进行，不影响 Flask 主线程的运行。

    用法示例：
        thread = Thread(target=send_async_email, args=(app, msg))
        thread.start()
    '''

    with app.app_context():  # 确保在 Flask 应用上下文中运行
        Mail(app).send(msg)  # 发送邮件


def send_email(user, email, tmp, token):
    '''
    发送邮件的主函数，参数分别是：
    当前登录用户, 收件人的邮箱, 前端文件名片段, token
    '''
    # 如果使用多线程，就不能用 current_app 了，它被看作是一个代理
    # 类似 socket 服务器中的主套接字，每次接收请求后都要创建一个临时套接字去处理
    # 此处使用 current_app 对象的 _get_curent_object 方法
    # 新创建的临时应用对象 app 包含独立的上下文信息，交给子线程处理
    app = current_app._get_current_object()
    print(f"邮件发件人: {app.config.get('MAIL_DEFAULT_SENDER')}")

    # Message 是一个类，它接收以下参数：
    # 1、默认参数 subject 字符串（邮件主题
    # 2、sender 字符串（发件人邮箱
    # 3、recipients 列表（收件人邮箱列表
    msg = Message(
            'To: ' + user.name, # 邮件主题
            sender = app.config.get('MAIL_DEFAULT_SENDER'), # 发件人邮箱
            recipients = [email]  # 收件人列表
    )

    '''
    特性:
    **Flask-Mail 支持 "multipart/alternative" 格式**
       - 这意味着 **`msg.body`（纯文本） 和 `msg.html`（HTML）属于同一封邮件的不同格式**。
       - 这样 **不会发送两次邮件**，邮件客户端会自动选择最合适的版本显示。

    **为什么提供 HTML 和 纯文本两种版本？**
       - **如果收件人的邮件客户端支持 HTML**，就会优先显示 `msg.html`（更美观）。
       - **如果收件人的邮件客户端不支持 HTML**（如部分旧设备或命令行客户端），则会回退到 `msg.body`（纯文本）。
       - **可以减少垃圾邮件过滤的风险**，某些邮件服务器可能会屏蔽纯 HTML 邮件，但如果有 `msg.body`（纯文本版本），更容易通过审核。
    '''

    msg.body = render_template('email/{}.txt'.format(tmp), user=user,
            token=token)    # 纯文本文件
    
    msg.html = render_template('email/{}.html'.format(tmp), user=user,
            token=token)    # HTML 文件
    
    thread = Thread(target=send_async_email, args=(app, msg))
    thread.start()          # 创建一个子线程并启动

    return thread
