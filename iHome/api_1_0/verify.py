# -*- coding:utf-8 -*-
from . import api
from iHome.utils.captcha.captcha import captcha
from flask import request, jsonify, make_response
from iHome import redis_store, constants
from iHome.response_code import RET


# 提供图片验证码和短信验证码
@api.route('/image_code')
def get_image_code():
    """
    # 生成图片验证码
    :return:
    """
    # 1.获取uuid(验证码编号)
    cur_id = request.args.get('cur_id')

    # 2.生成图片验证码
    name, text, data = captcha.generate_captcha()

    # 3.在redis中存储图片验证码
    try:
        redis_store.set('imagecode:%s' % cur_id, 'text', constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        print e
        return jsonify(errno=RET.DBERR, errmsg='保存图片验证码失败')
    # 4.返回验证码数据

    response = make_response(data)
    # 设置相应内容的的类型
    response.headers['Content-Type'] = 'image/jpg'
    return response

if __name__ == '__main__':
    get_image_code()
