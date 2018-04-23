#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from iHome.libs.yuntongxun.CCPRestSDK import REST
import ConfigParser

#���ʺ�
accountSid= '8aaf070862dcc47f0162ecedbc1407c8'

#���ʺ�Token
accountToken= 'ead1c72407114cbea884f66f749627c5'

#Ӧ��Id
appId='8aaf070862dcc47f0162ecedbc6f07ce'

#�����ַ����ʽ���£�����Ҫдhttp://
serverIP='app.cloopen.com'

#����˿� 
serverPort='8883'

#REST�汾��
softVersion='2013-12-26'

class CCP(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            # ����ʵ������
            obj = super(CCP, cls).__new__(cls, *args, **kwargs)
            cls._instance = obj
        return obj

    def __init__(self):
        # ��ʼ��ģ�����
        # ��ʼ��REST SDK
        self.rest = REST(serverIP, serverPort, softVersion)
        self.rest.setAccount(accountSid, accountToken)
        self.rest.setAppId(appId)

    def send_template_sms(self, to, datas, temp_id):
        # ����ģ�����
        # @param to �ֻ�����
        # @param datas �������� ��ʽΪ���� ���磺{'12','34'}���粻���滻���� ''
        # @param $tempId ģ��Id
        result = self.rest.sendTemplateSMS(to, datas, temp_id)
        if result.get('statusCode') == '000000':
            return 1
        else:
            return 0


   
#sendTemplateSMS(�ֻ�����,��������,ģ��Id)
if __name__ == "__main__":
    # ccp1 = CCP()
    # ccp2 = CCP()
    # print(id(ccp1),id(ccp2))

    CCP().send_template_sms('15202281385', ['100100','5'], 1)