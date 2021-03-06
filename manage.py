# -*- coding:utf-8 -*-

from flask_migrate import MigrateCommand, Migrate, Manager
from iHome import create_app,db, models

app = create_app('development')

# 创建manager对象
manager = Manager(app)
Migrate(app, db)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    # 运行开发web服务器
    print app.url_map
    manager.run()