# -*- coding:utf-8 -*-
import redis


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