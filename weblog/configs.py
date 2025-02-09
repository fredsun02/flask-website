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

class TestConfig(BaseConfig):
    pass



configs = {
    'dev': DevConfig,
    'test': TestConfig
}