# -*- coding:utf-8 -*-
# 此文件定义和房屋有关系的api
from . import api
from iHome.models import Area, House, Facility, HouseImage,Order
from iHome.response_code import RET
from flask import current_app, jsonify, request, g, session
from iHome.utils.commons import login_required
from iHome.utils.image_storage import image_storage
from iHome import db, constants, redis_store
import json
from datetime import datetime

@api.route('/users/houses')
@login_required
def get_user_houses():
    """
    获取用户发布的房屋信息:
    1. 根据登录id查询用户的所有房屋信息
    2. 组织数据，返回应答
    """
    # 1. 根据登录id查询用户的所有房屋信息
    user_id = g.user_id
    try:
        houses = House.query.filter(House.user_id == user_id).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋信息失败')

    # 2. 组织数据，返回应答
    # 组织数据
    houses_dict_li = []
    for house in houses:
        houses_dict_li.append(house.to_basic_dict())

    return jsonify(errno=RET.OK, errmsg='OK', data=houses_dict_li)



@api.route('/houses')
def get_house_list():
    """
    搜索房屋的信息:
    """
    print request.args
    area_id = request.args.get('aid')
    # new: 最新上线 booking: 入住最多 price-inc: 价格低->高 price-des: 价格高->低
    sort_key = request.args.get('sk', 'new')
    page = request.args.get('p')
    sd = request.args.get('sd')
    ed = request.args.get('ed')

    start_date = None
    end_date = None
    try:
        if area_id:
            area_id = int(area_id)

        page = int(page)

        if sd:
            start_date = datetime.strptime(sd, '%Y-%m-%d')

        if ed:
            end_date = datetime.strptime(ed, '%Y-%m-%d')

        if start_date and end_date:
            assert start_date < end_date, Exception('起始时间大于结束时间')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    # 尝试从缓存中获取搜索结果
    try:
        key = 'house:%s:%s:%s:%s' % (area_id, sd, ed, sort_key)
        res_json_str = redis_store.hget(key, page)
        if res_json_str:
            resp = json.loads(res_json_str)
            return jsonify(errno=RET.OK, errmsg='OK', data=resp)
    except Exception as e:
        current_app.logger.error(e)

    # 获取所有房屋的信息
    try:
        # houses = House.query.all()
        houses_query = House.query

        # 根据城区的id过滤房屋的信息，返回查询
        if area_id:
            houses_query = houses_query.filter(House.area_id == area_id)

        # 获取冲突订单
        try:
            conflict_orders_li = []
            if start_date and end_date:
                conflict_orders_li = Order.query.filter(end_date > Order.begin_date, start_date < Order.end_date).all()
            elif start_date:
                conflict_orders_li = Order.query.filter(start_date < Order.end_date).all()
            elif end_date:
                conflict_orders_li = Order.query.filter(end_date > Order.begin_date).all()

            if conflict_orders_li:
                # 获取冲突订单对应的房屋id
                conflict_houses_id = [order.house_id for order in conflict_orders_li]
                houses_query = houses_query.filter(House.id.notin_(conflict_houses_id))

        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='查询冲突订单失败')

        # 进行排序
        if sort_key == 'booking':
            houses_query = houses_query.order_by(House.order_count.desc())
        elif sort_key == 'price-inc':
            houses_query = houses_query.order_by(House.price)
        elif sort_key == 'price-des':
            houses_query = houses_query.order_by(House.price.desc())
        else:
            houses_query = houses_query.order_by(House.create_time.desc())

        # 分页操作
        house_paginate = houses_query.paginate(page, constants.HOUSE_LIST_PAGE_CAPACITY, False)
        # 获取当前页的结果列表
        houses = house_paginate.items
        # 获取分页之后的总页数
        total_page = house_paginate.pages

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋信息失败')

    # 组织数据
    houses_dict_li = []
    for house in houses:
        houses_dict_li.append(house.to_basic_dict())

    # 在redis中缓存数据
    resp = {'houses': houses_dict_li, 'total_page': total_page}
    try:
        key = 'house:%s:%s:%s:%s' % (area_id, sd, ed, sort_key)

        # 获取管道对象
        pipeline = redis_store.pipeline()
        # 开启redis事务
        pipeline.multi()
        # 向管道中添加执行命令
        pipeline.hset(key, page, json.dumps(resp))
        pipeline.expire(key, constants.HOUSE_LIST_REDIS_EXPIRES)
        # 提交redis事务
        pipeline.execute()
    except Exception as e:
        current_app.logger.error(e)

    # 返回应答
    return jsonify(errno=RET.OK, errmsg='OK', data=resp)

@api.route('/houses/index')
def get_houses_index():
    """
    获取首页展示房屋信息：
    1. 获取房屋的信息，按照创建时间进行降序排序，默认取前5个
    2. 组织数据，返回应答
    """
    # 1. 获取房屋的信息，按照创建时间进行降序排序，默认取前5个
    try:
        houses = House.query.order_by(House.create_time.desc()).limit(constants.HOME_PAGE_MAX_HOUSES).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取房屋信息失败')

    # 2. 组织数据，返回应答
    houses_dict_li = []
    for house in houses:
        houses_dict_li.append(house.to_basic_dict())

    return jsonify(errno=RET.OK, errmsg='OK', data=houses_dict_li)


@api.route('/house/<int:house_id>')
def get_house_info(house_id):
    """
    获取房屋的详情信息:
    1. 根据房屋id获取房屋信息（如果查不到，代表房屋不存在)
    2. 组织数据，返回应答
    """
    # 1. 根据房屋id获取房屋信息（如果查不到，代表房屋不存在)
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋信息失败')

    if not house:
        return jsonify(errno=RET.NODATA, errmsg='房屋不存在')

    # 2. 组织数据，返回应答
    # 尝试从session获取user_id, 如果取不到，返回-1
    user_id = session.get('user_id', -1)

    return jsonify(errno=RET.OK, errmsg='OK', data={'house': house.to_full_dict(), 'user_id': user_id})

@api.route('/houses/image', methods=["POST"])
@login_required
def save_house_image():
    """
    上传房屋的图片:
    1. 接收房屋的id 和 房屋图片文件 并进行参数校验
    2. 上传房屋的图片到七牛云
    3. 创建HouseImage对象并保存房屋图片信息
    4. 添加房屋图片信息到数据库
    5. 返回应答
    """
    # 1. 接收房屋的id 和 房屋图片文件 并进行参数校验
    house_id = request.form.get('house_id')

    if not house_id:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')

    file = request.files.get('house_image')

    if not file:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')

    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋信息失败')

    if not house:
        return jsonify(errno=RET.NODATA, errmsg='房屋不存在')

    # 2. 上传房屋的图片到七牛云
    try:
        key = image_storage(file.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传房屋图片失败')

    # 3. 创建HouseImage对象并保存房屋图片信息
    house_image = HouseImage()
    house_image.house_id = house_id
    house_image.url = key

    # 判断当前房屋是否有默认的图片，如果没有，进行添加
    if not house.index_image_url:
        house.index_image_url = key

    # 4. 添加房屋图片信息到数据库
    try:
        db.session.add(house_image)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存房屋图片信息失败')

    # 5. 返回应答
    img_url = constants.QINIU_DOMIN_PREFIX + key
    return jsonify(errno=RET.OK, errmsg='OK', data={'img_url': img_url})

@api.route('/areas')
def get_areas():
    """
    获取城区信息：
    """
    # 1. 从数据库中获取所有的城区信息
    # 先尝试从缓存中获取城区的信息，如果获取到，直接返回，如果获取不到，再去查询数据库
    try:
        area_json_str = redis_store.get("ares")
        if area_json_str:
            areas_dict_li = json.loads(area_json_str)
            return jsonify(errno=RET.OK, errmsg='OK', data=areas_dict_li)
    except Exception as e:
        current_app.logger.error(e)

    try:
        areas = Area.query.all()
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DBERR, errmsg='查询城区信息失败')

    # 2. 组织数据，返回应答
    areas_dict_li = []
    for area in areas:
        areas_dict_li.append(area.to_dict())

    # redis设置缓存
    try:
        redis_store.set("areas", json.dumps(areas_dict_li), constants.AREA_INFO_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)


    return jsonify(errno=RET.OK, errmsg='OK', data=areas_dict_li)


@api.route('/houses', methods=["POST"])
@login_required
def save_new_house():
    """
    发布新房源:
    1. 接收房屋的基本信息并进行参数校验
    2. 创建House对象并保存房屋基本信息
    3. 将房屋的基本信息添加进数据库
    4. 返回应答
    """
    # 1. 接收房屋的基本信息并进行参数校验
    req_dict = request.json

    title = req_dict.get('title')
    price = req_dict.get('price') # 房屋价格
    address = req_dict.get('address')
    area_id = req_dict.get('area_id')
    room_count = req_dict.get('room_count')
    acreage = req_dict.get('acreage')
    unit = req_dict.get('unit')
    capacity = req_dict.get('capacity')
    beds = req_dict.get('beds')
    deposit = req_dict.get('deposit') # 房屋押金
    min_days = req_dict.get('min_days')
    max_days = req_dict.get('max_days')

    if not all([title, price, address, area_id, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')

    try:
        # 数据库中房屋的价格和押金以 分 保存
        price = float(price) * 100
        deposit = float(deposit) * 100
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    # 2. 创建House对象并保存房屋基本信息
    house = House()
    house.user_id = g.user_id
    house.area_id = area_id
    house.title = title
    house.price = price
    house.address = address
    house.room_count = room_count
    house.acreage = acreage
    house.unit = unit
    house.capacity = capacity
    house.beds = beds
    house.deposit = deposit
    house.min_days = min_days
    house.max_days = max_days

    # 获取房屋的设施信息
    facility = req_dict.get('facility') # [1, 3, 4]

    try:
        facilities = Facility.query.filter(Facility.id.in_(facility)).all()
        if facilities:
            house.facilities = facilities
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取房屋设施信息失败')

    # 3. 将房屋的基本信息添加进数据库
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存房屋信息失败')

    # 4. 返回应答
    return jsonify(errno=RET.OK, errmsg='OK', data={'house_id': house.id})
