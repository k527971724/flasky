from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config#包含四个项的字典
from flask_login import LoginManager
from flask_pagedown import PageDown


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()


login_manager = LoginManager()
login_manager.session_protection = 'strong'#安全等级，防止用户会话遭篡改
login_manager.login_view = 'auth.login' #



#定义工厂函数（根据参数不同，可以创建多个不同配置的实例）
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])#配置app
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)
    
    #将main蓝本注册到程序上（注册到app上后蓝本才成为程序的一部分）
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    #将auth蓝本注册到程序上
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
                                        #为路由的url增加前缀
                                        
    #将api蓝本注册到程序上
    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')
    
    
    #与前端测试用的蓝本
    from .api_1_1 import cooperation
    app.register_blueprint(cooperation, url_prefix='/api/cooperation')
    
    
    return app

