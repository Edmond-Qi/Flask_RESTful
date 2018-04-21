# -*- coding:utf-8 -*-
from . import api
from iHome import redis_store

@api.route('/',methods=['POST','GET'])
def index():
    # 测试redis
    redis_store.set('name', 'laowang')
    # session['name'] = 'smart'
    return 'haha'