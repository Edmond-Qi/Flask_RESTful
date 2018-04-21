# -*- coding:utf-8 -*-
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
# from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate, Manager
from config import Config

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