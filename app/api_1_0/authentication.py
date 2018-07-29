#除浏览器之外的客户端很难提供对cookie的支持
#而REST要求无状态，所以使用Flask-HTTPAuth认证用户
from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from ..models import User
from . import api
from .errors import unauthorized, forbidden


#由于这种用户认证方法只在API蓝本中使用
#所以Flask-HTTPAuth扩展只在蓝本包中初始化
#而不像其他扩展那样要在程序包中初始化
auth = HTTPBasicAuth()

#【返回布尔值，并更新current_user】
@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':#如果email_or_token为空，匿名用户
        return False
    if password == '':#如果password为空，email_or_token提供的是令牌
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    
    #如果两个参数都不为空，使用常规邮件和密码验证
    user = User.query.filter_by(email=email_or_token).first()
    if not user:#未注册
        return False
    else:
        g.current_user = user
        g.current_used = False
        return user.verify_password(password)


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@api.before_request
@auth.login_required
def before_request():
    #非匿名用户，未认证
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed account')

#【生成认证令牌】
@api.route('/tokens/', methods=['POST'])
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invilad credentials')
    else:
        return jsonify(
            {'token': g.current_user.generate_auth_token(expiration=3600),
            'expiration': 3600})













