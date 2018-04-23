# -*- coding:utf-8 -*-
import json
import random
import re

from iHome.models import User
from . import api
from iHome.utils.captcha.captcha import captcha
from flask import request, jsonify, make_response, current_app, session
from iHome import redis_store, constants
from iHome.response_code import RET
from iHome.utils.SendTemplateSMS import CCP


@api.route('/session', methods=['POST'])
def login():
    """
    用户登录功能：
    :return:
    """
    # 1. 获取参数（手机号，密码）并参数校验
    req_dict = request.json
    mobile = req_dict.get('mobile')
    password = req_dict.get('password')

    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    if not re.match(r'^1[3456789]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式不正确')

    # 2. 根据手机号查询用户的信息（如果查询不到，用户不存在）
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户信息失败')

    if not user:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')

    # 3. 校验用户的密码是否正确，如果正确
    if not user.check_user_passsword(password):
        return jsonify(errno=RET.PWDERR, errmsg='登录密码错误')

    # 4. 在session中记录用户的登录状态
    session['user_id'] = user.id
    session['username'] = user.name
    session['mobile'] = user.mobile

    # 5. 返回应答，登录成功
    return jsonify(errno=RET.OK, errmsg='登录成功')




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
    image_code = req_dict.get('image_code')
    image_code_id = req_dict.get('image_code_id')

    # 2.判断参数的完整性并且进行参数校验
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg=' ')

    if not re.match(r'1[3456789]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式不正确')

    # 3.从redis中获取对应的图片验证码
    try:
        real_image_code = redis_store.get('imagecode:%s' % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询图片验证码错误')
    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg='图片验证码已过期')
    # 4.对比图片验证码
    image_code = image_code.encode("utf-8")
    if real_image_code != image_code:
        return jsonify(errno=RET.DATAERR, errmsg='图片验证码错误')
    # 5.发送短信通知
    # 生成短信验证码
    sms_code = '%06d' % random.randint(0,999999) #333
    # 发送短信验证码
    res = CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES/60], 1)

    if res !=1:
        return jsonify(errno=RET.THIRDERR, errmsg="发送短信失败")
    try:
        redis_store.set('sms_code:%s' % mobile,sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存验证码失败')
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
        redis_store.set('imagecode:%s' % cur_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
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
