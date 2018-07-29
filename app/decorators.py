'''
Python装饰器（decorator）在实现的时候，
被装饰后的函数其实已经是另外一个函数了（函数名等函数属性会发生改变），
为了不影响，Python的functools包中提供了一个叫wraps的decorator
来消除这样的副作用。写一个decorator的时候，
最好在实现之前加上functools的wrap，它能保留原有函数的名称和docstring。
'''

from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):#如果当前用户没有某个权限
                abort(403)#返回错误403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
    

def admin_required(f):
    return permission_required(Permission.ADMIN)(f)

























