# -*- coding: utf-8 -*-
# encoding: utf-8
'''
@author: kane
A utility tool to send short message from message queue.
'''
from django.core.management.base import NoArgsCommand
from billiards import bcms
import logging
from django.utils.timezone import localtime, now
from django.utils import simplejson
from billiards.commons import decodeunicode
from billiards.models import BcmsMessage
import requests
import abc

logger = logging.getLogger("billiards-bcms")
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

class MessageException(Exception):
    pass

class MsgProcess(NoArgsCommand):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def getBcms(self):
        pass
    
    @abc.abstractmethod
    def sendMessage(self, msg):
        pass
    
    def handle(self, *args, **options):
        logger.info('[%s]Start to process messages in queue.' %(localtime(now()).strftime(TIME_FORMAT)))
        bcmsmsg = self.getBcms()
        try:
            while True:
                msgs = bcms.fetch(bcmsmsg.lastMsgId if bcmsmsg != None else 7800)
                if msgs is not None:
                    if 'error_code' in msgs:
                        if msgs['error_code'] == 30011:
                            logger.info("[%s]Fetched 0 messages from queue since msg_id %s." %(localtime(now()).strftime(TIME_FORMAT), bcmsmsg.lastMsgId))
                        else:
                            logger.error("[%s]BCMS complains \'%s\' when fetching messages from queue since msg_id %s." %(localtime(now()).strftime(TIME_FORMAT), msgs['error_msg'], bcmsmsg.lastMsgId))
                        break
                    else:
                        lastMsgid = 0
                        logger.info('[%s]Fetched %s messages from queue since msg_id %s.' %(localtime(now()).strftime(TIME_FORMAT), msgs['response_params']['message_num'], bcmsmsg.lastMsgId))
                        for msg in msgs['response_params']['messages']:
                            logger.info('[%s]Processing message \'%s\' with content \'%s\'' %(localtime(now()).strftime(TIME_FORMAT), msg['msg_id'], msg['message']))
                            lastMsgid = long(msg['msg_id'])
                            try:
                                data = simplejson.loads(msg['message'])
                                self.sendMessage(data)
                            except ValueError, e:
                                logger.error('[%s]Failed to parse message as json due to %s.' %(localtime(now()).strftime(TIME_FORMAT), str(e)))
                                logger.exception(e)
                                raise MessageException(e)
                            except ImportError:
                                logger.error('[%s]Failed to call method \'%s\' for generating message content.' %(localtime(now()).strftime(TIME_FORMAT), data['method']))
                                logger.exception(e)
                                raise MessageException(e)
                            
                            logger.info('[%s]Updating last message %s already processed.' %(localtime(now()).strftime(TIME_FORMAT), lastMsgid))
                            bcmsmsg.lastMsgId = lastMsgid + 1
                            bcmsmsg.save()
                        
                        if len(msgs['response_params']['messages']) < 10:
                            break
                else:
                    logger.error("[%s]Unknown error occurred when fetching messages from queue since msg_id %s." %(localtime(now()).strftime(TIME_FORMAT), bcmsmsg.lastMsgId))
                    break
        except MessageException, e:
            logger.error("[%s]Stopped process message due to fail to send short message." %(localtime(now()).strftime(TIME_FORMAT)))
            
class Command(MsgProcess):
    help = 'Process short message from message queue'

    def __call(self, function_string, *args):
        import importlib
        mod_name, func_name = function_string.rsplit('.',1)
        mod = importlib.import_module(mod_name)
        func = getattr(mod, func_name)
        return func(*args)
    
    def __hsSendMsg(self, number, content):
        gateway = 'http://service2.hongshutech.com:8080/sms_send2.do'
        r = requests.post(gateway, data={'corp_id': '7150121001', 'corp_pwd': 'hj1001', 'corp_service': '1069yd', 
                        'mobile': str(number), 'msg_content': content.encode('gbk')}, 
                      headers={"Content-Type": "application/x-www-form-urlencoded;charset=gbk"})
        if r.status_code == requests.codes.ok:
            response = r.text
            logger.debug(response)
            if response.startswith('0#'):
                logger.info("\tSuccessed to send short message.")
            else:
                logger.error("\tFailed to send short message due to %s." %(response))
                raise MessageException(response)
        else:
            logger.error("\tFailed to send short message due to unavailable of HS gateway.")
            raise MessageException(response)
        
    def getBcms(self):
        return BcmsMessage.objects.get(target=BcmsMessage.SHORT_MESSAGE)
    
    def sendMessage(self, msg):
        cellphone = msg['number']
        logger.info('[%s]Sending message \'%s\' to number %s' %(localtime(now()).strftime(TIME_FORMAT), decodeunicode(msg['msg']), cellphone))
        data = simplejson.loads(msg['msg'])
        messagecontent = self.__call(data['method'], data)
        logger.debug(messagecontent)
        self.__hsSendMsg(cellphone, messagecontent)
