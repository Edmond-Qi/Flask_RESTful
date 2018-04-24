# -*- coding:utf-8 -*-
# 自定义路由转换器
from werkzeug.routing import BaseConverter
from flask import session, jsonify, g
from iHome.response_code import RET
import functools

class RegexConverter(BaseConverter):
    def __init__(self, url_map, regex):
        super(RegexConverter, self).__init__(url_map)
        self.regex = regex

def login_required(view_func):
    """登录验证装饰器"""
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        # 尝试从session中获取user_id
        user_id = session.get('user_id')

        if user_id:
            # 用户已登录
            # 使用g变量临时保存user_id, g变量临时保存的内容可以在每个请求开始到请求结束的过程中使用
            # 这里使用g变量临时保存user_id，在后续的api代码中就不需要再次从session中获取user_id
            g.user_id = user_id
            return view_func(*args, **kwargs)
        else:
            # 用户未登录
            return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')

    return wrapper

