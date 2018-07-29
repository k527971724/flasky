from flask import render_template, request, jsonify
from . import main


@main.app_errorhandler(403)#禁止：认证密令无权访问
def forbidden(e):
    #内容协商机制（）
    #检查Accept请求部首，为接受json而不接受html的客户端返回json
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response#为不接受html的客户端返回json
        
    return render_template('403.html'), 403

            
@main.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    return render_template('500.html'), 500
