from flask import jsonify
from app.exceptions import ValidationError
from . import api

#不是返回html，而是返回response，response包含json

def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


@api.errorhandler(ValidationError)#只要抛出了指定类的异常，就会调用被修饰的函数
def validation_error(e):
    return bad_request(e.args[0])
