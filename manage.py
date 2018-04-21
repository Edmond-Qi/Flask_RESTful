# -*- coding:utf-8 -*-
from flask import Flask

class Config(object):
    """"""
    DEBUG = True

# 创建Flask应用程序实例
app = Flask(__name__)

# 从加载配置
app.config.from_object(Config)

@app.route('/')
def index():
    return 'haha'

if __name__ == '__main__':
    # 运行开发web服务器
    app.run()