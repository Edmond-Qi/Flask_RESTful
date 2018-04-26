# -*- coding:utf-8 -*-
# 此文件中定义和订单相关api
from datetime import datetime

from flask import current_app
from flask import g
from flask import request, jsonify

from iHome import db
from iHome.models import House, Order
from iHome.response_code import RET
from iHome.utils.commons import login_required
from . import api


@api.route('/orders/<int:order_id>/comment', methods=['PUT'])
@login_required
def save_order_comment(order_id):
    """
    保存订单的评论的信息:
    1. 接收评论参数并进行参数校验
    2. 根据订单id查询订单的信息(如果查询不到，说明订单不存在)
    3. 更改订单的状态并设置评论，然后更新数据库
    4. 返回应答
    """
    # 1. 接收评论参数并进行参数校验
    req_dict = request.json
    comment = req_dict.get('comment')

    if not comment:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')

    # 2. 根据订单id查询订单的信息(如果查询不到，说明订单不存在)
    try:
        order = Order.query.filter(Order.id == order_id,
                                   Order.user_id == g.user_id,
                                   Order.status == 'WAIT_COMMENT').first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询订单信息失败')

    if not order:
        return jsonify(errno=RET.NODATA, errmsg='订单不存在')

    # 3. 更改订单的状态并设置评论，然后更新数据库
    order.comment = comment
    order.status = 'COMPLETE'

    # 4. 更新数据库中数据
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存订单信息失败')

    # 5. 返回应答
    return jsonify(errno=RET.OK, errmsg='OK')


# /orders/<int:order_id>/status?action=accept|reject
@api.route('/orders/<int:order_id>/status', methods=['PUT'])
@login_required
def update_order_status(order_id):
    """
    进行接单或者拒单操作：
    1. 接收参数action并进行校验，action==accept(接单) action==reject(拒单)
    2. 根据订单的id去查询订单的信息(如果查询不到，说明订单不存在)
    3. 根据action设置订单的状态，(如果是拒单，需要接收拒单原因)
    4. 更新数据库中数据
    5. 返回应答
    """
    # 1. 接收参数action并进行校验，action==accept(接单) action==reject(拒单)
    action = request.args.get('action')
    if action not in ('accept', 'reject'):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    # 2. 根据订单的id去查询订单的信息(如果查询不到，说明订单不存在)
    try:
        # 找到订单对应的房屋的房东
        order = Order.query.filter(Order.id == order_id,
                                   Order.status == 'WAIT_ACCEPT').first()  # 订单的状态必须处于待接单的状态

        # 获取房东id
        landlord_id = order.house.user_id

        # 判断当前登录的用户是否是房东
        if landlord_id != g.user_id:
            # 不是房东
            return jsonify(errno=RET.DATAERR, errmsg='不是房东')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询订单失败')

    if not order:
        return jsonify(errno=RET.NODATA, errmsg='订单不存在')

    # 3. 根据action设置订单的状态，(如果是拒单，需要接收拒单原因)
    if action == 'accept':
        # 接单
        order.status = 'WAIT_COMMENT'  # 待评价
    else:
        # 拒单
        # 接收拒单原因
        req_dict = request.json
        reason = req_dict.get('reason')
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')

        order.comment = reason
        order.status = 'REJECTED'

    # 4. 更新数据库中数据
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存订单信息失败')

    # 5. 返回应答
    return jsonify(errno=RET.OK, errmsg='OK')


# /orders?role=lodger
# role=lodger, 代表以房客的身份查询预订其他人房屋的订单
# role=landlord, 代表以房东的身份查询其他人预订自己房屋的订单
@api.route('/orders')
@login_required
def get_order_list():
    """
    获取用户的订单信息:
    1. 获取查询订单时用户的身份
        1.1 如果role==lodger, 代表以房客的身份查询预订其他人房屋的订单
        1.2 如果role=landlord, 代表以房东的身份查询其他人预订自己房屋的订单
    2. 组织数据，返回应答
    """
    # 1. 获取查询订单时用户的身份
    role = request.args.get('role')
    if role not in ('lodger', 'landlord'):
        return jsonify(errno=RET.PARAMERR, errmsg='数据错误')

    user_id = g.user_id

    try:
        if role == 'lodger':
            # 1.1 如果role==lodger, 代表以房客的身份查询预订其他人房屋的订单
            orders = Order.query.filter(Order.user_id == user_id).all()
        else:
            # 1.2 如果role=landlord, 代表以房东的身份查询其他人预订自己房屋的订单
            # 获取房东的所有房屋的信息
            houses = House.query.filter(House.user_id == user_id).all()
            houses_id_li = [house.id for house in houses]
            # 查询出订单中房屋的id在houses_id_li列表中的数据
            orders = Order.query.filter(Order.house_id.in_(houses_id_li)).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询订单信息失败')

    # 2. 组织数据，返回应答
    orders_dict_li = []
    for order in orders:
        orders_dict_li.append(order.to_dict())

    return jsonify(errno=RET.OK, errmsg='OK', data=orders_dict_li)

@api.route('/orders', methods=['POST'])
@login_required
def save_order_info():
    """
    保存房屋预订订单的信息:
    1. 接收参数(房屋id, 起始时间，结束时间) 并进行参数校验
    2. 根据房屋id查询房屋信息（如果查不到，说明房屋信息不存在)
    3. 根据入住起始时间和结束时间查询订单是否有冲突
    4. 创建Order对象并保存订单信息
    5. 把订单信息添加进数据库
    6. 返回应答，订单创建成功
    """
    # 1. 接收参数(房屋id, 起始时间，结束时间) 并进行参数校验
    req_dict = request.json
    house_id = req_dict.get('house_id')
    start_date = req_dict.get('start_date')
    end_date = req_dict.get('end_date')

    if not all([house_id, start_date, end_date]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        assert start_date < end_date, Exception('起始时间大于结束时间')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    # 2. 根据房屋id查询房屋信息（如果查不到，说明房屋信息不存在)
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋信息失败')

    if not house:
        return jsonify(errno=RET.NODATA, errmsg='房屋不存在')

    # 3. 根据入住起始时间和结束时间查询订单是否有冲突
    try:
        conflict_orders_count = Order.query.filter(end_date > Order.begin_date,
                                                   start_date < Order.end_date,
                                                   Order.house_id == house_id).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询冲突订单失败')

    if conflict_orders_count > 0:
        # 存在冲突订单
        return jsonify(errno=RET.DATAERR, errmsg='房屋已被预订')

    # 4. 创建Order对象并保存订单信息
    days = (end_date - start_date).days
    order = Order()
    order.user_id = g.user_id
    order.house_id = house_id
    order.begin_date = start_date
    order.end_date = end_date
    order.days = days
    order.house_price = house.price
    order.amount = house.price * days

    # 房屋预订量加1
    house.order_count += 1

    # 5. 把订单信息添加进数据库
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存订单信息失败')

    # 6. 返回应答，订单创建成功
    return jsonify(errno=RET.OK, errmsg='OK')