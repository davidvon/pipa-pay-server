# -*- coding: utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler
import datetime
import time
from flask import g
from flask import Flask, request, session
from flask.ext.login import current_user
from flask.ext.security.forms import ChangePasswordForm
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.babelex import Babel, Domain
from flask.ext.mail import Mail
from flask.ext.security import Security, SQLAlchemyUserDatastore, ForgotPasswordForm
from flask.ext.restful import Api as Restful_Api
import config
import redis
import sys

app = Flask(__name__)
app.config.from_object('config')
app.is_online = False

handler = RotatingFileHandler(config.LOG_FILE, config.LOG_MODE, config.LOG_MAX_SIZE, config.LOG_MAX_FILES)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

redis_client = redis.StrictRedis(host='127.0.0.1', port=6379)
logger.info("[RUNNING] running mode:[%r], database:[%r]" % (config.RUN_MODE, config.SQLALCHEMY_DATABASE_URI))

db = SQLAlchemy(app)
babel = Babel(app, default_locale=config.BABEL_DEFAULT_LOCALE, default_domain=Domain(domain='admin'))
mail = Mail(app)
restful_api = Restful_Api(app)


@babel.localeselector
def get_locale():
    override = request.args.get('lang')
    if override:
        session['lang'] = override
    return session.get('lang', config.BABEL_DEFAULT_LOCALE)


reload(sys)
sys.setdefaultencoding('utf-8')
from models import User, Role, Order
from app.security.login_forms import ExtendedRegisterForm, LoginForm

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore,
                    register_form=ExtendedRegisterForm,
                    login_form=LoginForm,
                    forgot_password_form=ForgotPasswordForm,
                    change_password_form=ChangePasswordForm)


@app.before_request
def before_request():
    g.session = db.session
    g.user = current_user


@app.teardown_request
def teardown_request(exception):
    g.session.close()


@app.before_first_request
def before_first_request():
    if not Role.query.filter_by(name=config.ROLE_ADMIN).first():
        role_admin = Role(name=config.ROLE_ADMIN, desc='管理员')
        db.session.add(role_admin)
        db.session.add(Role(name=config.ROLE_SHOP_STAFF, desc='店员'))
        db.session.commit()


import view
import views
import api

db.create_all()
