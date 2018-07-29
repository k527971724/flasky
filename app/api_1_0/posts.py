from flask import jsonify, request, g, url_for, current_app
from .. import db
from ..models import Post, Permission
from . import api
from .decorators import permission_required
from .errors import forbidden

'''
#【文章集合，GET】获得文章集合
@api.route('/posts/')
@auth.login_required
def get_posts():
    posts = Post.query.all()
    return jsonify({'posts': [post.to_json() for post in posts]})
    #返回返回Post的列表
'''

#【分页文章资源】
@api.route('/posts/')
def get_posts():
    page = request.args.get('page', 1, type=int)
    #参数：返回第几页，每页多少条信息（默认20）
    pagination = Post.query.paginate(page,
        per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
        #请求的页数超出了范围，True则会返回404错误，False返回空列表
    posts = pagination.items#当前页面的所有项目
    prev = None#上一页的url
    next = None#下一页的url
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1)
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total})


#【文章，GET】获取一片篇文章
@api.route('/posts/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())

    
#【文章，POST】上传一篇文章
@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE)
def new_post():
    post = Post.from_json(request.json)#??
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, \
        {'Location': url_for('api.get_post', id=post.id)}

        
#【文章，PUT】更新已有文章
@api.route('/posts/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE)
def edit_post(id):
    post = Post.query.get_or_404(id)
    #判断当前用户与文章作者是否匹配
    if g.current_user != post.author and \
            not g.current_user.can(Permission.ADMIN):
        return forbidden('Insufficient permissions')
    else:
        post.body = request.json.get('body', post.body)
        db.session.add(post)
        db.session.commit()
        return jsonify(post.to_json)
        #向客户端返回更新的文章，使客户端不用再发起一次GET请求






















