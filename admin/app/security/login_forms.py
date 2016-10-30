# -*- coding: utf-8 -*-
from flask_security.forms import RegisterForm, Required, Length, Form, \
    NextFormMixin, get_form_field_label, \
    PasswordField, BooleanField, SubmitField, get_message, verify_and_update_password, requires_confirmation
from wtforms import TextField
from flask.ext.babel import gettext as _
from models import User
from sqlalchemy import func


class ExtendedRegisterForm(RegisterForm):
    nickname = TextField(_('nickname'),
                         [Required(message='NICKNAME_NOT_PROVIDED'),
                          Length(min=5, max=25, message='NICKNAME_INVALID_LENGTH')])


class LoginForm(Form, NextFormMixin):
    nickname = TextField(get_form_field_label('nickname'))
    password = PasswordField(get_form_field_label('password'))
    remember = BooleanField(get_form_field_label('remember_me'))
    submit = SubmitField(get_form_field_label('login'))

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

    def validate(self):
        if not super(LoginForm, self).validate():
            return False

        if self.nickname.data.strip() == '':
            self.nickname.errors.append(get_message('NICKNAME_NOT_PROVIDED')[0])
            return False

        if self.password.data.strip() == '':
            self.password.errors.append(get_message('PASSWORD_NOT_PROVIDED')[0])
            return False

        self.user = User.query.filter(func.lower(User.nickname) == func.lower(self.nickname.data)).first()

        if self.user is None:
            self.nickname.errors.append(get_message('USER_DOES_NOT_EXIST')[0])
            return False
        if not verify_and_update_password(self.password.data, self.user):
            self.password.errors.append(get_message('INVALID_PASSWORD')[0])
            return False
        if requires_confirmation(self.user):
            self.nickname.errors.append(get_message('CONFIRMATION_REQUIRED')[0])
            return False
        if not self.user.is_active():
            self.nickname.errors.append(get_message('DISABLED_ACCOUNT')[0])
            return False
        return True