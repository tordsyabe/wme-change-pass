from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, EqualTo, Length, Regexp


class AuthForm(FlaskForm):

    email = EmailField("Email", [InputRequired(message="Email field is required")])
    password = PasswordField("Password", [InputRequired(message="Password field is required")])
    recaptcha = RecaptchaField()


class ChangePassForm(FlaskForm):

    new_pass = PasswordField("Password", [InputRequired(message="Password field is required"), EqualTo(
        "confirm_pass", message='Passwords must match'), Length(12, message="Password must be more than 12 characters"), Regexp("^(?=.*?[A-Z])(?=(.*[a-z]){1,})(?=(.*[\d]){1,})(?=(.*[\W]){1,})(?!.*\s).{12,}$", message="Password must combination of letters, symbols and numbers")])
    confirm_pass = PasswordField(
        "Confirm Password", [InputRequired()])


class UserDetailForm(FlaskForm):

    user_email = EmailField("Email", [InputRequired(message="Email field is required")])
    user_password = StringField("Password", [InputRequired(message="Password field is required")])
