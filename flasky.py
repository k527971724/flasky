import os
from app import create_app, db
from app.models import User, Role
from flask_script import Manager, Server, Shell
from flask_migrate import Migrate,MigrateCommand

#创建程序实例，FLASK_CONFIG中是开发模式，default是
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

#context 上下文，语境
@manager.shell
#打开命令行时进行默认导入
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)
    #数据库模型在上面添加


manager.add_command("server", Server())
manager.add_command("shell", Shell(make_context=make_shell_context ))
manager.add_command("db", MigrateCommand)
#python manage.py server 运行服务器
#python manage.py shell  运行命令行并进行默认导入
#python manage.py db     运行命令行并使用SQLAlchemy


#用户直接运行当前件时：
if __name__ == '__main__':
    print("直接运行manager.run()")
    manager.run()
