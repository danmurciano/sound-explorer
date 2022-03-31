from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SearchField
from wtforms_alchemy import model_form_factory
from models import db, User
from wtforms.validators import InputRequired, Length, NumberRange, Email

BaseModelForm = model_form_factory(FlaskForm)

class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session

class RegisterForm(ModelForm):
    class Meta:
        model = User


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=3, max=20)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6, max=20)])

class SearchSongForm(FlaskForm):
    # title = StringField("Song Title", validators=[InputRequired(), Length(max=50)])
    popularity = SelectField("Popularity", choices=[("any", "Any"), ("popular", "Popular"),("obscure", "Obscure")])
    limit = SelectField("Results", choices=[(20),(40),(60)])


class DeleteForm(FlaskForm):
    """No fields are required"""
