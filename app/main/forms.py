from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError
from ..models import Role, User
#PageDown是客户端 Markdown 到 HTML 的转换程序
from flask_pagedown.fields import PageDownField#和TextAreaField接口一致


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), 
                                            Length(1,64), 
                                            Email()])
    username = StringField('Username', validators=[DataRequired(),
                                                    Length(1,64),
                Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                'Usernames must have only letters, numbers, dots or '
                'underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)#字段内容必须是int
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')
    
    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)#父类
        self.role.choices = [(role.id, role.name)
                            for role in Role.query.order_by(Role.name).all()]
        self.user = user
        
    def validate_email(self, field):#修改邮箱时不能与数据库拥有邮箱重名
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class PostForm(FlaskForm):
    #body = TextAreaField("What's in your mind?", validators=[DataRequired()])
    body = PageDownField("What's on your mind?", validators=[DataRequired()])
    submit = SubmitField('Submit')


















