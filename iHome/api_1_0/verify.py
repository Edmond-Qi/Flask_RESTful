# -*- coding:utf-8 -*-
from . import api
from iHome.utils.captcha.captcha import captcha


# 提供图片验证码和短信验证码
@api.route('/image_code')
def get_image_code():
    """
    生成图片验证码
    :return:
    """
    name, text, data = captcha.generate_captcha()
    return data

if __name__ == '__main__':
    get_image_code()
