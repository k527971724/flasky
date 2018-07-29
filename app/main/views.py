from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, jsonify
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm
from .. import db
from ..models import Role, User, Permission, Post
from ..decorators import admin_required

#测试用,可以删掉
@main.route('/ajax', methods=['GET', 'POST'])#定义了两种方法
def connectAjax():
    return render_template('test3.html')





#【主页】
@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    #validate_on_submit会调用表单字段中validators的所有限制条件
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
                    #current_user是对User的封装
                    #方法_get_current_object返还User对象（注意函数前的_）
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    
    #渲染的页数从请求的查询字符串（request.args）中获取，默认渲染第一页    
    page = request.args.get('page', 1, type=int)
    #paginate() 方法返回一个Pagination 类对象，在Flask-SQLAlchemy 中定义
    #包含很多属性，用于在模板中生成分页链接，因此将其作为参数传入了模板
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
            page, 
            per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
    posts = pagination.items   
    return render_template('single-post.html')
    #return render_template('index.html', form=form, posts=posts,
    #                        pagination=pagination)
    

#【显示用户资料】
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    #一对多反向关系的用法:
    posts = user.posts.order_by(Post.timestamp.desc()).all()#多篇文章
    return render_template('user.html', user=user, posts=posts)
    
    
#【用户级的资料编辑器】
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


#【管理员级的资料编辑器（管理员编辑用户资料，用户id是参数）】
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)
    

#【访问单篇博客】
@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', posts=[post])
    #post.html 模板接收一个列表作为参数，这个列表就是要渲染的文章
    #_posts.html 模板才能在这个页面中使用
    
    
#【修改博客】
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMIN):
        abort(403)#403权限错误
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)