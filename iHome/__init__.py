# -*- coding:utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from config import config_dict
from utils.commons import RegexConverter

# 创建db对象
db = SQLAlchemy()
redis_store = None

def create_app(config_name):
    # 创建Flask应用程序实例
    app = Flask(__name__)

    Config = config_dict[config_name]

    # 从加载配置
    app.config.from_object(Config)

    # db对象关联app
    db.init_app(app)

    # redis
    global redis_store
    redis_store = redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)

    # 开启csrf保护
    CSRFProtect(app)

    # session存储
    Session(app)

    # 添加路由转换器
    app.url_map.converters['re'] = RegexConverter

    from iHome.api_1_0 import api
    app.register_blueprint(api, url_prefix='/api/v1.0')
    from iHome.web_html import html
    app.register_blueprint(html)

    return app