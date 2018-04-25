# -*- coding:utf-8 -*-
from flask import Blueprint


api = Blueprint("iHome", __name__)

# from index import index
# from verify import get_image_code
# from passport import register

from . import index, passport, verify, profile, house