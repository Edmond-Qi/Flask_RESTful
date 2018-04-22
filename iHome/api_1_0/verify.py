# -*- coding:utf-8 -*-
import json
import re
from . import api
from iHome.utils.captcha.captcha import captcha
from flask import request, jsonify, make_response, current_app
from iHome import redis_store, constants
from iHome.response_code import RET


@api.route('/sms_code',methods=['POST'])
def send_sms_code():
    """
    发送短信息验证码
    :return:
    """
    # 1.获取参数（手机号，图片验证码，图片验证码id）
    # 获取json
    req_data = request.data
    req_dict = json.loads(req_data)

    mobile = req_dict.get('mobile')
    image_code = req_dict.get('imageCode')
    image_code_id = req_dict.get('imageCodeId')

    # 2.判断参数的完整性并且进行参数校验
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    if not re.match(r'1[3456789]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式不正确')

    # 3.从redis中获取对应的图片验证码
    try:
        real_image_id = redis_store.get('imagecode:%s' % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询图片验证码错误')
    if not real_image_id:
        return jsonify(errno=RET.NODATA, errmsg='图片验证码已过期')
    # 4.对比图片验证码
    if real_image_id != image_code_id:
        return jsonify(errno=RET.DATAERR, errmsg='图片验证码错误')
    # 5.发送短信通知　todo

    # 6.返回消息
    return jsonify(errno=RET.OK, errmsg='发送短信成功')

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
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存图片验证码失败')
    # 4.返回验证码数据

    response = make_response(data)
    # 设置相应内容的的类型
    response.headers['Content-Type'] = 'image/jpg'
    return response

if __name__ == '__main__':
    get_image_code()
