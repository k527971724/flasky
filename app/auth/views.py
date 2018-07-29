from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, \
                        login_required, \
                        current_user
from . import auth#蓝本
from .. import db
from ..models import User
from ..email import send_email
from .forms import LoginForm, RegistrationForm
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app

#【请求钩子】
@auth.before_app_request#在蓝本中使用针对程序全局的请求钩子，每次请求前运行
def before_request():
    if current_user.is_authenticated:
        current_user.ping()#每次请求都会更新last_seen
        #未确认，蓝本不是'auth'，端点不是'static'
        if not current_user.confirmed \
                and request.endpoint \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            print("before_request重定向到auth.unconfirmed")
            return redirect(url_for('auth.unconfirmed'))


#【用户登录】
#注册路由时，增加了url_prefix='/auth'
@auth.route('/login', methods=['GET', 'POST'])
def login():
    print("login")
    form = LoginForm()
    if form.validate_on_submit():#请求是POST，尝试登录用户
        #检查用户是否已注册（email名是否存在）
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            if user.verify_password(form.password.data):
                #在用户会话中将用户标记为已登录，函数由flask_login提供
                login_user(user, form.remember_me.data)#长效cookie
                next = request.args.get('next')#把登录前的地址保存在next中
                #如果没有之前的地址，就使用首页
                if next is None or not next.startswith('/'):
                    next = url_for('main.index')
                return redirect(next)#重定向
            else:
                flash('Invalid password.')
        else:
            flash('Invalid username.')
    return render_template('auth/login.html', form=form)#请求是GET，直接渲染模板
    #这是template文件夹下的auth/login.html


#【用户登出】
@auth.route('/logout')
@login_required#路由保护，没登录的用户会被发往登录页面
def logout():
    print("logout")
    logout_user()#函数由flask_login提供
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


#【用户注册】
@auth.route('/register', methods=['GET', 'POST'])
def register():
    print("register")
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        
        #发送邮件
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account', 
                    'auth/email/confirm',
                    user=user, token=token)#最后几项是模板和向模板传参
        flash('请求确认邮件已经发送到您的邮箱')
        db.session.commit()#成功发送邮件之后再提交数据库
        print("redirect to url_for('main.index')")
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


#【邮件确认用户】
@auth.route('/confirm/<token>')#尖括号部分是动态部分，作为参数传入
@login_required#??
def confirm(token):
    print("cnfirm--<token>")
    if current_user.confirmed:#已经过确认就不能在访问了
        return redirect(url_for('main.index'))
    
    if current_user.confirm(token):#确认成功(confirm函数负责向数据库提交)
        db.session.commit()#需要提交
        print("token认证成功")
        flash('You have confirmed your account. Thanks!')
    else:#确认失败
        print("token认证失败")
        flash('The confirmation link is invalid or has expired.')
        
    return redirect(url_for('main.index'))#无论成功失败都返回主页

        
#【未确认】
@auth.route('/unconfirmed')
def unconfirmed():#只有未确认用户可以访问，匿名用户和已确认用户不可以访问
    print("uncomfirmed")
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    
    return render_template('auth/unconfirmed.html')#显示重新发送的链接


#【重新发送邮件】
@auth.route('/confirm')#这个URL和上面的不同，没有token部分的内容
@login_required
def resend_confirmation():
    print("comfirm--resend_confirmation")
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account', 
            'auth/email/confirm',
            user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))













