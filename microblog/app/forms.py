from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, TextAreaField, StringField
from wtforms.validators import Required, Length, InputRequired
from .models import User

class LoginForm(Form):
    openid = TextField('openid', validators = [Required()])
    remember_me = BooleanField('remember_me', default = False)
    
class EditForm(Form):
    nickname = TextField('username', validators = [Required()])
    firstname = TextField('firstname', validators = [Required()])
    lastname = TextField('lastname', validators = [Required()])
    country = TextField('country',validators = [Required()])
    state = TextField('state',validators = [Required()])
    city = TextField('city',validators = [Required()])
    area = TextField('area',validators = [Required()])
    phone = TextField('phone', validators = [Required()])
    about_me = TextAreaField('about_me', validators = [Length(min = 0, max = 300)])

    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not Form.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user != None:
            self.nickname.errors.append('This nickname is already in use. Please choose another one.')
            return False
        return True

class RatingsForm(Form):
    comment = TextField('comment', validators = [Required()])
    rates = TextField('rates',validators = [Required()])

class MessagesForm(Form):
    text = TextField('text',validators = [Required()])

class SearchForm(Form):
    state = StringField('state', validators=[InputRequired()])
    city = StringField('city', validators=[InputRequired()])
    activity = StringField('activity', validators=[InputRequired()])

