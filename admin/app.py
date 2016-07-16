# -*- coding: utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, g
from flask.ext.login import current_user
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api as RestfulApi

import config

app = Flask(__name__)
app.config.from_object('config')

handler = RotatingFileHandler(config.LOG_FILE, config.LOG_MODE, config.LOG_MAX_SIZE, config.LOG_MAX_FILES)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)


@app.before_request
def before_request():
    g.session = db.session
    g.user = current_user


@app.teardown_request
def teardown_request(exception):
    g.session.close()

import redis
redis_client = redis.StrictRedis(host=config.REDIS_SERVER_IP, password=config.REDIS_SERVER_PWD,
                                 db=config.REDIS_SERVER_DB, port=6379)
logger.info("[RUNNING] running mode: %s" % config.RUN_MODE)
logger.info("[RUNNING] db: [%r], redis: [%r,%r,%d]" % (config.SQLALCHEMY_DATABASE_URI, config.REDIS_SERVER_IP,
                                                       config.REDIS_SERVER_PWD, config.REDIS_SERVER_DB))
logger.info("[RUNNING] app id:%s, secret:%s" % (config.WEIXIN_APPID, config.WEIXIN_SECRET))

restful_api = RestfulApi(app)

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

db = SQLAlchemy(app)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


import models
import api

db.create_all()