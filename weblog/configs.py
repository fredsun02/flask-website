import os

class BaseConfig:
    """
    基础配置类
    """

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'asdfasdf'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  

class DevConfig(BaseConfig):
    '''
    开发阶段使用的配置类
    '''

    '''
    连接数据库的配置项
    '''
    url = 'mysql://root{}@localhost/weblog?charset=utf8'
    pwd = os.environ.get('MYSQL_PWD')
    pwd = ':{}'.format(pwd) if pwd else ''
    SQLALCHEMY_DATABASE_URI = url.format(pwd)    

    # 用gmail作为测试邮箱服务器
    # ！！！BUG未解决
    # smtplib.SMTPSenderRefused: (530, b'5.7.0 Authentication Required.
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_SSL = False
    MAIL_USE_TLS = True 
    MAIL_DEFAULT_SENDER = "sunshen02@gmail.com"

    # 需要提前将 MAIL_USERNAME 和 MAIL_PASSWORD 设置为环境变量
    # 对于 Gmail 而言，MAIL_PASSWORD 为 16 位的应用专用密码
    # 详见 https://support.google.com/accounts/answer/185833?hl=zh-Hans
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')


class TestConfig(BaseConfig):
    pass



configs = {
    'dev': DevConfig,
    'test': TestConfig
}