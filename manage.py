# -*- coding:utf-8 -*-
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate


class Config(object):
    """配置文件"""
    DEBUG = True

    # 设置secret key
    SECRET_KEY = '8j/iuN4cb2PCokc9rqYdfekUaRne2mUDR6mrGjuGwwhtN8kXGsUdixnjG2xP0DlT'

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/ihome26"
    # 关闭数据库修改追踪
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # redis配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # session存储设置
    # 设置session存储到redis中
    SESSION_TYPE = 'redis'
    # 设置存储session的redis地址
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    # 设置session的信息加密
    SESSION_USE_SIGNER = True
    # 设置session的过期时间
    PERMANENT_SESSION_LIFETIME = 86400 * 2


# 创建Flask应用程序实例
app = Flask(__name__)


# 从加载配置
app.config.from_object(Config)

# 创建db对象
db = SQLAlchemy(app)

# redis
redis_store = redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)

# 开启csrf保护
CSRFProtect(app)

# session存储
Session(app)

# 创建manager对象
manager = Manager(app)
Migrate(app, db)

manager.add_command('db', MigrateCommand)

@app.route('/',methods=['POST','GET'])
def index():
    # 测试redis
    # redis_store.set('name', 'laowang')
    # session['name'] = 'smart'
    return 'haha'

if __name__ == '__main__':
    # 运行开发web服务器
    manager.run()