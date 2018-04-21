# -*- coding:utf-8 -*-
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from config import config_dict

# 创建db对象
db = SQLAlchemy()

def create_app(config_name):
    # 创建Flask应用程序实例
    app = Flask(__name__)

    Config = config_dict[config_name]

    # 从加载配置
    app.config.from_object(Config)

    # db对象关联app
    db.init_app(app)

    # redis
    redis_store = redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)

    # 开启csrf保护
    CSRFProtect(app)

    # session存储
    Session(app)

    return app