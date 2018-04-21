# -*- coding:utf-8 -*-

from flask_migrate import MigrateCommand, Migrate, Manager
from iHome import app, db

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