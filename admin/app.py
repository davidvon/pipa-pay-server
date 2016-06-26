# -*- coding: utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api as Restful_Api

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

restful_api = Restful_Api(app)

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

db = SQLAlchemy(app)
db.create_all()

import api


