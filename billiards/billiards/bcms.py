# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2014年3月9日

@author: kane
'''
import time
from billiards import settings
import json
import hashlib
from django.utils.http import urlencode, urlquote_plus
import logging
import requests
from requests.exceptions import HTTPError
from django.utils import simplejson

BCMS_BASIC_REST_URL = 'http://bcms.api.duapp.com/rest/2.0/bcms/%s'
QUEUE_NAME = 'dfbee5593a7498d87f504b9faa99f2d2'
BCMS_REST_URL = BCMS_BASIC_REST_URL %(QUEUE_NAME)

logger = logging.getLogger("billiards-bcms")

def getRequiredParameters():
    paras = {
        'timestamp': int(time.time()),
        'client_id': settings.BAE_IMAGE['key']
    }
    return paras

def queryString(delimeter, paras):
    return delimeter.join(['%s=%s' % (key, value) for (key, value) in sorted(paras.items())])

def calcSign(paras, queue=QUEUE_NAME, secret=settings.BAE_IMAGE['secret']):
    basicstring = 'POST%s%s%s' %(BCMS_BASIC_REST_URL %(queue), queryString('', paras), secret)
#     print "basic string: %s" %(basicstring)
    encodedstring = urlquote_plus(basicstring)
#     print "encoded string: %s" %(encodedstring)
    return hashlib.md5(encodedstring).hexdigest()

def doBCMSRequest(paras):
    paras['sign'] = calcSign(paras)
    data = urlencode(paras)
    req = requests.post(BCMS_REST_URL, data=data, headers=
                        {'Host': 'bcms.api.duapp.com', 'Accept-Encoding': 'identity','Content-Type': 'application/x-www-form-urlencoded'})
    if req.status_code == requests.codes.ok:
        jobj = req.json()
        logger.debug(jobj)
        return jobj
    else:
        try:
            req.raise_for_status()
        except HTTPError, e:
            logger.info("Failed to make bcms REST API call due to '%s'", str(e))
            return req.json()
        return None
    
def mail(address, subject, message, fromaddress=None):
    paras = getRequiredParameters()
    paras['method'] = 'mail'
    paras['message'] = message
    paras['mail_subject'] = subject
    paras['address'] = json.dumps(address)
    if fromaddress is not None:
        paras['from'] = fromaddress
    doBCMSRequest(paras)    
    
def publish(message):
    paras = getRequiredParameters()
    paras['method'] = 'publish'
    paras['message'] = message
    doBCMSRequest(paras)
    
def fetch(msgid):
    paras = getRequiredParameters()
    paras['method'] = 'fetch'
    paras['fetch_num'] = 10
    paras['msg_id'] = msgid
    return doBCMSRequest(paras)
'''
Not working
'''
def confirmMessage(msgid, timeout = int(time.time())):
    paras = getRequiredParameters()
    paras['method'] = 'confirmmsg'
    paras['msg_timeout'] = timeout
    paras['msg_id'] = msgid
    return doBCMSRequest(paras)
'''
Not working
'''
def deleteMessage(msgid):
    paras = getRequiredParameters()
    paras['method'] = 'deletemessagebyid'
    paras['msg_id'] = msgid
    return doBCMSRequest(paras)
'''
Not working
'''
def deleteMessages(msgs):
    paras = getRequiredParameters()
    paras['method'] = 'deletemessagesbyids'
    paras['msg_id'] = simplejson.dumps(msgs)
    return doBCMSRequest(paras)
    
if __name__ == '__main__':
#     params = {}
#     params['client_id'] = '6E820afd87518a475f83e8a279c0d367'
#     params['message'] = 'HelloWorld'
#     params['method'] = 'publish'
#     params['timestamp'] = 1329472104
#     print calcSign(params, '9569d9de1004fde88458838c19e8a687', '259eea423dee18c7b865b0777cd657cc')
    mail(['42470522@qq.com'], 'test email', 'A mail is sent by BCMS.', 'ibilliards@163.com')