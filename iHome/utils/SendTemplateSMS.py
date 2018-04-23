#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from iHome.libs.yuntongxun.CCPRestSDK import REST
import ConfigParser

#主帐号
accountSid= '8aaf070862dcc47f0162ecedbc1407c8'

#主帐号Token
accountToken= 'ead1c72407114cbea884f66f749627c5'

#应用Id
appId='8aaf070862dcc47f0162ecedbc6f07ce'

#请求地址，格式如下，不需要写http://
serverIP='app.cloopen.com'

#请求端口 
serverPort='8883'

#REST版本号
softVersion='2013-12-26'

class CCP(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            # 创建实例对象
            obj = super(CCP, cls).__new__(cls, *args, **kwargs)
            cls._instance = obj
        return obj

    def __init__(self):
        # 初始化模板短信
        # 初始化REST SDK
        self.rest = REST(serverIP, serverPort, softVersion)
        self.rest.setAccount(accountSid, accountToken)
        self.rest.setAppId(appId)

    def send_template_sms(self, to, datas, temp_id):
        # 发送模板短信
        # @param to 手机号码
        # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
        # @param $tempId 模板Id
        result = self.rest.sendTemplateSMS(to, datas, temp_id)
        if result.get('statusCode') == '000000':
            return 1
        else:
            return 0


   
#sendTemplateSMS(手机号码,内容数据,模板Id)
if __name__ == "__main__":
    # ccp1 = CCP()
    # ccp2 = CCP()
    # print(id(ccp1),id(ccp2))

    CCP().send_template_sms('15202281385', ['100100','5'], 1)