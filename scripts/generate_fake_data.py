'''
终端命令行执行
python3 -m scripts.generate_fake_data
生成测试数据，该脚本可多次执行
'''

from faker import Faker
from random import randint
from manage import app

# 启动应用的上下文环境
app.app_context().push()

from weblog.models import db, Role, User, Blog


Role.insert_roles()                                         # 创建角色
default_role = Role.query.filter_by(default=True).first()   # 默认角色
fake = Faker('zh-cn')                                       # 创建虚拟数据的工具


def iter_users():
    '''创建 10 个虚拟用户'''
    for i in range(10):
        user = User(
                name = fake.name(),
                age = randint(11, 30),
                gender = ['MALE', 'FEMALE'][randint(0, 1)],
                location = fake.city_name(),
                email = fake.email(),
                phone_number = fake.phone_number(),
                role = default_role,
                password = 'shiyanlou',
                about_me = fake.sentence(nb_words=2),
                confirmed = 1
        )
        user.avatar_hash = user.gravatar()
        yield user


def iter_blogs():
    '''为每个虚拟用户创建数个虚拟博客'''
    for user in iter_users():
        db.session.add(user)
        for i in range(1, 6):
            blog = Blog(
                    author = user,
                    time_stamp = fake.date_time_this_year()
            )
            blog.body = fake.text(max_nb_chars=20)
            yield blog


def run():
    for blog in iter_blogs():
        db.session.add(blog)
    db.session.commit()
    print('OK')


if __name__ == '__main__':
    run()
