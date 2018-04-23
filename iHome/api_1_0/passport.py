# -*- coding:utf-8 -*-
from . import api
from flask import request,jsonify, current_app, session
from iHome.response_code import RET
from iHome import redis_store,db
from iHome.models import User


@api.route('/users', methods=['POST'])
def register():
    """
    注册用户功能

    2.从redis中获取短信验证码（如果获取不到说明短信验证码过期）
    3.对比短信验证码
    4.创建用户信息到数据库
    5.返回应答，提示注册成功
    :return:
    """
    # 1.获取请求中的参数
    req_dict = request.json
    mobile = req_dict.get('mobile')
    phonecode = req_dict.get('phonecode')
    password = req_dict.get('password')

    if not all([mobile, phonecode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    # 2. 从redis中获取短信验证码（如果获取不到，短信验证码过期)
    try:
        sms_code = redis_store.get('sms_code:%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询短信验证码失败')

    if not sms_code:
        return jsonify(errno=RET.NODATA, errmsg='短信验证码已过期')

    # 3. 对比短信验证码，如果一致
    if sms_code != phonecode:
        return jsonify(errno=RET.DATAERR, errmsg='短信验证码错误')
        # 4. 创建User并保存注册用户的信息
    user = User()
    user.mobile = mobile
    # 用户名默认使用注册手机号
    user.name = mobile
    # 注册密码加密保存
    user.password = password

    # 5. 添加用户信息到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存用户信息失败')

    # 用户注册成功之后记录用户的登陆状态
    session['user_id'] = user.id
    session['user_name'] = user.name
    session['mobile'] = user.mobile

    # 6. 返回应答，告诉注册成功
    return jsonify(errno=RET.OK, errmsg='注册成功')