# -*- coding:utf-8 -*-
from flask import Blueprint


api = Blueprint("iHome", __name__)

from index import index