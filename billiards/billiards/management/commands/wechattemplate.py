# -*- coding: utf-8 -*-
# encoding: utf-8
'''
@author: kane
A utility tool to send wechat notification from message queue.
'''
import logging
from django.utils.timezone import localtime, now
from django.utils import simplejson
from billiards.commons import decodeunicode
from billiards.management.commands.msgprocessor import MsgProcess, TIME_FORMAT
from django.contrib.auth.models import User
from billiards.client import Client

logger = logging.getLogger("billiards-bcms")

class Command(MsgProcess):
    help = 'Process wechat notification from message queue'
    
    def __init__(self):
        super(Command, self).__init__()
        from billiards.models import WechatCredential
        cred = WechatCredential.objects.first()
        self.client = Client(cred.appid, cred.secret)
    
    def getBcms(self):
        from billiards.models import BcmsMessage
        return BcmsMessage.objects.get(target=BcmsMessage.WECHAT_TEMPLATE)
    
    def sendMessage(self, msg):
        logger.info('[%s]Sending message \'%s\' via wechat.' %(localtime(now()).strftime(TIME_FORMAT), decodeunicode(msg['msg'])))
        data = simplejson.loads(msg['msg'])
        user = User.objects.get(username=data['user_id'])
        if user.site_name.startswith('wechat'):
            messagecontent = self.__call(data['method'], data, user)
            if messagecontent is None:
                logger.info('%s is not a wechat user, ignore this message' %(data['user_id']))
            else:
                logger.debug(messagecontent)
                response = self.client.message_template(messagecontent.encode('utf-8'))
                if 'errcode' in response and response['errcode'] == 0:
                    logger.info('Successfully sent wechat notification to user %s.' %(str(user)))
                else:
                    logger.warning('Failed to send wechat notfication to user %s with message \'%s\'' %(str(user), response['errmsg']))
        else:
            logger.info('%s is not a wechat user, ignore this message' %(data['user_id']))

    def __call(self, function_string, *args):
        import importlib
        mod_name, func_name = function_string.rsplit('.',1)
        mod = importlib.import_module(mod_name.replace("assistant", "wechat_template"))
        func = getattr(mod, func_name)
        return func(*args)
    
