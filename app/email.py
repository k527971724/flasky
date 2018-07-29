from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

#参数：目标邮箱，主题，显示模板
def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    #参数：标题，发送者邮箱（只是显示的信息，不能设定发送者），接收者邮箱
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], 
                  recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    #异步发送邮件
    thr = Thread(target=send_async_email, args=[app, msg])#线程
    thr.start()
    return thr

