from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, HiddenField, TextAreaField
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


class SearchSongForm(FlaskForm):
    popularity = SelectField("Popularity", choices=[("any", "Any"), ("high", "High"),("low", "Low"),("obscure", "Obscure")])
    limit = SelectField("Results", choices=[(20),(50),(100)])


class SavePlaylistForm(FlaskForm):
    plName = StringField(validators=[InputRequired(), Length(max=100)])
    plDescription = TextAreaField(validators=[Length(max=250)])
