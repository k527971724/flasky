from . import cooperation
from flask import jsonify
from .. import db
from ..models import Post
import json

#实现资源端点
#http --json http://127.0.0.1:5000/api/cooperation/test/108
@cooperation.route('/test/<int:id>')
def get_post(id):
    post=Post.query.get_or_404(id)
    body = post.body
    #return json.dumps({'json':id, 'body':body})
    return  jsonify({'json':id, 'body':body})














