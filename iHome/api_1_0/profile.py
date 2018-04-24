# -*- coding:utf-8 -*-
from iHome.models import User
from . import api
from flask import session, current_app, jsonify,request,g
from iHome.response_code import RET
from iHome.utils.image_storage import image_storage
from iHome import db, constants
from iHome.utils.commons import login_required


@api.route('/user/auth', methods=['POST'])
@login_required
def set_user_auth():
    """
    用户实名认证功能:
    0. todo: 判断用户是否登录
    1. 获取提交的真实姓名和身份证号并进行参数校验
    2. todo: 使用第三方接口
    3. 设置用户的实名认证信息
    4. 返回应答
    """
    # 1. 获取提交的真实姓名和身份证号并进行参数校验
    req_dict = request.json
    real_name = req_dict.get('real_name')
    id_card = req_dict.get('id_card')

    if not all([real_name, id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    # 2. todo: 使用第三方接口
    # 3. 设置用户的实名认证信息
    user_id = g.user_id

    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户信息失败')

    if not user:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')

    # 判断用户是否已经实名认证
    if user.real_name and user.id_card:
        return jsonify(errno=RET.DATAEXIST, errmsg='已经实名认证')

    user.real_name = real_name
    user.id_card = id_card

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='设置实名信息失败')

    # 4. 返回应答
    return jsonify(errno=RET.OK, errmsg='实名认证成功')

@api.route('/user/name', methods=['PUT'])
@login_required
def set_user_name():
    """
    设置用户的用户名:
    0. 判断用户是否登录
    1. 接收用户名并进行校验
    2. 设置用户的用户名
    3. 返回应答
    """
    # 1. 接收用户名并进行校验
    req_dict = request.json
    username = req_dict.get('username')

    if not username:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')

    # 2. 设置用户的用户名
    # user_id = session.get('user_id')
    user_id = g.user_id

    # 校验用户名是否已存在
    try:
        user = User.query.filter(User.name == username, User.id != user_id).first()
    except Exception as e:
        user = None
        current_app.logger.error(e)

    if user:
        # 用户名已存在
        return jsonify(errno=RET.DATAEXIST, errmsg='用户名已存在')

    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户信息失败')

    if not user:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')

    user.name = username

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='设置用户名失败')

    # 3. 返回应答
    return jsonify(errno=RET.OK, errmsg='设置用户名成功')


@api.route('/user/avatar', methods=['POST'])
@login_required
def set_user_avatar():
    """
    保存上传用户的头像:
    0. 判断用户是否登录
    1. 获取上传头像文件
    2. 上传头像文件到七牛云系统
    3. 设置用户的头像记录
    4. 返回应答，上传头像成功
    """
    # 1. 获取上传头像文件
    file = request.files.get('avatar')

    if not file:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')

    # 2. 上传头像文件到七牛云系统
    try:
        key = image_storage(file.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传头像失败')

    # 3. 设置用户的头像记录
    # user_id = session.get('user_id')
    user_id = g.user_id

    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户信息失败')

    if not user:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')

    user.avatar_url = key

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存头像记录失败')

    # 4. 返回应答，上传头像成功
    avatar_url = constants.QINIU_DOMIN_PREFIX + key
    return jsonify(errno=RET.OK, errmsg='上传头像成功', data={'avatar_url': avatar_url})


@api.route('/user')
@login_required
def get_user_info():
    """
    获取用户的个人信息
    # 0. 判断用户是否登陆
    # 1. 获取当前登陆用户的id
    # 2. 根据id获取用户的信息（如果查不到，说明用户不存在）
    # 3. 组织数据，返回应答
    """
    # 1. 获取当前登陆用户的id
    # user_id = session.get('user_id')
    user_id = g.user_id

    # 2. 根据id获取用户的信息（如果查不到，说明用户不存在）
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户信息失败')

    if not user:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')

    # 3. 组织数据，返回应答
    # resp = {
    #     'user_id': user.id,
    #     'username': user.name,
    #     'avatar_url': constants.QINIU_DOMIN_PREFIX + (user.avatar_url if user.avatar_url else '')
    # }
    return jsonify(errno=RET.OK, errmsg='OK', data=user.to_dict())