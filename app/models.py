from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown#服务器端 Markdown到 HTML 的转换
import bleach#HTML 清理器
from flask import request, current_app, url_for
from flask_login import UserMixin, AnonymousUserMixin
from app.exceptions import ValidationError
from . import db, login_manager




#【权限常量】
class Permission:
    FOLLOW = 1               #关注00000001
    COMMENT = 2              #评论00000010
    WRITE = 4                #写文章
    MODERATE = 8             #管理评论
    ADMIN = 16               #管理员

#【用户角色】
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    #反向关系，User对象可以通过role访问本对象
    #本对象可以通过users访问所有关联的User对象
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)#??
        if self.permissions is None:
            self.permissions = 0
                
  
    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT,
                          Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT,
                              Permission.WRITE, Permission.MODERATE,
                              Permission.ADMIN],
        }#想要修改角色权限或添加新角色，只要修改roles字典后运行函数即可
        default_role = 'User'#默认角色是User
        for r in roles.keys():
            role = Role.query.filter_by(name=r).first()
            if role is None:#如果数据库里没有这个角色
                role =Role(name=r)
            #设置role.permissions字段
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            #设置role.default字段
            role.default = (role.name == default_role)#角色是否是默认角色
            db.session.add(role)
        db.session.commit()
    
    def add_permission(self, perm):#增加一个权限
        if not self.has_permission(perm):
            self.permissions += perm
    
    def remove_permission(self, perm):#减少一个权限
        if self.has_permission(perm):
            self.permissions -= perm
            
    def reset_permissions(self):#全部权限置零
        self.permissions = 0
    
    def has_permission(self, perm):#判断一个权限是否已有
        return self.permissions & perm == perm
        
    def __repr__(self):
        return '<Role %r>' % self.name


#【用户】
#使用Flask-Login扩展，需要模型类拥有4个方法，通过继承UserMixin直接实现
class User(UserMixin, db.Model):
    __tablename__ = 'users'#表名
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    #一对多关系，一个role_id对应多个User
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    #反向关系，Post对象可以通过author访问本对象
    #本对象可以通过posts访问关联的所有Post对象
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    #注册确认
    confirmed = db.Column(db.Boolean, default=False)#这一列默认值为False
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    #自我介绍
    about_me = db.Column(db.Text())
    #注册日期
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    #最后访问时间
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    #MD5散列值
    avatar_hash = db.Column(db.String(32))
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        '''
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
                #并没有提交数据库，临时赋予用户管理员权限？
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        '''
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()
    
    #【密码】
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    #【生成确认令牌】
    #expiration截止时间（秒）
    #返回确认令牌同token
    def generate_confirmation_token(self, expiration=3600):#
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm':self.id})
    
    
    #【#判断令牌是否正确】
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        
        #令牌没有办法生成id
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        
        if data.get('confirm') != self.id:#令牌生成的id与用户id不一致
            return False 
        else:
            self.confirmed = True
            db.session.add(self)
            return True
    
    
    #【判断角色权限】
    #perm某一项权限
    #返回布尔值
    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)
    
    #【判断角色是否是管理员】
    #返回布尔值
    def is_administrator(self):
        return self.can(Permission.ADMIN)
        
        
    #【更新最后访问时间】
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()
    
    
    #【生成email的MD5散列值】
    #返回email的MD5散列值
    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        
        
    #【生成头像URL】
    #size图像像素 g图像级别
    #返回头像URL
    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or self.gravatar_hash()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)
    
    
    #【REST：支持基于令牌的认证】
    #【REST: 1、生成认证令牌】使用编码后的用户id 字段值生成一个签名令牌
    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('utf-8')
        
        
    #【REST： 2、验证认证令牌】
    @staticmethod#静态方法，因为只有解码令牌后才能知道用户是谁
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])#根据主键返回行对象
    
    
    
    def to_json(self):
        json_user = {#【相对URL？】
            'url': url_for('api.get_user', id=self.id),
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'posts_url': url_for('api.get_user_posts', id=self.id),
            'followed_posts_url': url_for('api.get_user_followed_posts',
                                          id=self.id),
            'post_count': self.posts.count()
        }
        return json_user
    
    def __repr__(self):
        return '<User %r>' % self.username


#【匿名用户】所有不在数据库里的用户都是匿名用户
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):#没有任何权限
        return False
    
    def is_administrator(self):#不是管理员
        return False


#???????
login_manager.anonymous_user = AnonymousUser

#Flask-Login要求实现的加载用户的回调函数（使用指定标识符加载用户）
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    #get方法返回主键对应的行
    

#【博客文章】
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True )
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)#文章内容的HTML版本
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    #一对多关系，一个author_id对应多个Post
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    @staticmethod
    #把Markdown 格式的博客文章转换成HTML
    def on_changed_body(target, value, oldvalue, initiator):
        #THML标签白名单
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        #target应该是Post对象
        target.body_html = bleach.linkify(
                bleach.clean(markdown(value, output_format='html'),
                tags=allowed_tags, 
                strip=True))
        #markdown()函数把Markdown文本转成HTML
        #bleach.clean()函数删除不在白名单中的标签
        #bleach.linkify()函数把纯文本中的URL转成<a>链接
        
    #【把文章转化成JSON格式的序列化字典】
    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author_url': url_for('api.get_user', id=self.author_id, _external=True),
            #'comments_url': url_for('api.get_post_comments', id=self.id, _external=True),
            #'comment_count': self.comments.count()
        }
        return json_post
    #【JSON格式转Post】
    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        return Post(body=body)
        '''
        只要body 属性的值发生变化，就会生成body_html
        无需指定timestamp 属性
        由于客户端无权选择博客文章的作者，所以没有使用author 字段
        comments 和comment_count 属性使用数据库关系自动生成
        '''
#on_changed_body 函数注册在body 字段上，是SQLAlchemy“set”事件的监听程序
#这意味着只要这个类实例的body 字段设了新值，函数就会自动被调用
db.event.listen(Post.body, 'set', Post.on_changed_body)
    
    
    
    
    
    
    
    
    
    
    
    

    
