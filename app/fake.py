from random import randint#生成指定范围内的整数，包括上下限
from sqlalchemy.exc import IntegrityError#except异常，IntegrityError完整性错误
from faker import Faker
from . import db
from .models import User, Post


#【生成用户数据】默认生成100个
def users(count=100):
    fake = Faker()
    #fake=Faker(locale='zh_CN')#数据的文化选项，默认'en_US'
    i = 0
    while i < count:
        u = User(email=fake.email(),
                 username=fake.user_name(),
                 password='password',
                 confirmed=True,
                 name=fake.name(),
                 location=fake.city(),
                 about_me=fake.text(),
                 member_since=fake.past_date())
        db.session.add(u)
        try:
            db.session.commit()
            i += 1  #插入成功了才会自增，所以一定会达到要求的个数
            print(i)
        except IntegrityError:
            db.session.rollback()#产生IntegrityError异常则回滚
            print('rollback')

def posts(count=100):
    fake = Faker()
    user_count = User.query.count()#用户总数
    for i in range(count):
        #随机偏移量，取第一条数据
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Post(body=fake.text(),
        timestamp=fake.past_date(),
        author=u)
        db.session.add(p)
    db.session.commit()




























