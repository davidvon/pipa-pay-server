# -*- coding: utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
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

import redis
app.is_online = False
redis_client = redis.StrictRedis(host='127.0.0.1', port=6379)
logger.info("[RUNNING] status: online [%r], test [%r], database [%r]" %
            (config.IS_ONLINE, config.UNITTEST, config.SQLALCHEMY_DATABASE_URI))

restful_api = RestfulApi(app)

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

db = SQLAlchemy(app)
db.create_all()

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

import api


