'''
200 成功
201 已创建
400 坏请求
401 未授权
403 禁止
404 未找到（由flask生成，返回HTML）
405 不允许使用的方法
500 内部服务器错误（由flask生成，返回HTML）
'''

def forbidden(message):
    response = jsonify({
        'error':'forbidden',
        'message':message})
    response.status_code = 403
    return response
































