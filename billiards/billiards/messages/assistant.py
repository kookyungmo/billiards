# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2015年2月21日

@author: kane
'''
from datetime import datetime
from billiards.models import DATETIME_FORMAT
from django.utils.timezone import localtime
import pytz
from billiards.settings import TIME_ZONE
ORDER_CONFIRMATION=u'【我为台球狂】您的订单已确认，请您准时到场消费。\n\
预约助教：%s\n\
预约时间：%s，%s点-%s点；\n\
预约时长：%s小时\n\
预约单价：%s元/小时\n\
预约球房：%s；\n\
球房地址：%s \n\
消费金额：%s元；\n\
消费时，请将您的消费码告知助教。\n\
感谢您使用教练预约平台。\n\
请在【我为台球狂】微信公众平台—我的订单，查看预约详情。'

ORDER_PAY_SUCCESS=u'【我为台球狂】我们已经收到您的订单，等待助教确认。\n\
预约时间：%s（明天），%s点-%s点；\n\
预约球房：%s；\n\
球房地址：%s\n\
消费金额：%s元；\n\
感谢您使用教练预约平台。\n\
请在【我为台球狂】微信公众平台—我的订单查看预约详情。'

ORDER_COMPLETE=u'【我为台球狂】您的订单已消费。\n\
消费时间：%s，%s\n\
感谢您使用教练预约平台。\n\
请在【我为台球狂】微信公众平台—我的订单查看预约详情。'

ORDER_ARRIVAL=u'【我为台球狂】有您的一个预约订单，回复“OK”确认接单；回复“NO”拒绝接单。\n\
预约助教：%s\n\
预约时间：%s，%s点-%s点；\n\
预约球房：%s；\n\
消费金额：%s元；\n\
客户微信昵称：%s\n\
客户联系电话：%s\n\
消费时，请向客户索要消费码，并发送给【我为台球狂】微信公众平台。'

DATE_FORMAT = u'%Y年%m月%d日'.encode('utf-8')
TIME_FORMAT = u'%H'.encode('utf-8')
TIME2_FORMAT = u'%H点%m分'.encode('utf-8')

def orderConfirmationMsg(order):
    starttime = datetime.strptime(order['starttime'], DATETIME_FORMAT)
    return ORDER_CONFIRMATION %(order['assistant_name'], starttime.strftime(DATE_FORMAT).decode('utf-8'), starttime.strftime(TIME_FORMAT).decode('utf-8'),
            datetime.strptime(order['endtime'], DATETIME_FORMAT).strftime(TIME_FORMAT).decode('utf-8'), order['duration'], order['price'],
            order['poolroom_name'], order['poolroom_address'], order['payment'])
    
def orderPaySuccess(order):
    starttime = datetime.strptime(order['starttime'], DATETIME_FORMAT)
    return ORDER_PAY_SUCCESS %(starttime.strftime(DATE_FORMAT).decode('utf-8'), starttime.strftime(TIME_FORMAT).decode('utf-8'),
            datetime.strptime(order['endtime'], DATETIME_FORMAT).strftime(TIME_FORMAT).decode('utf-8'),
            order['poolroom_name'], order['poolroom_address'], order['payment'])
    
def orderComplete(order):
    completetime = localtime(datetime.utcfromtimestamp(order['timestamp']), pytz.timezone(TIME_ZONE))
    return ORDER_COMPLETE %(completetime.strftime(DATE_FORMAT).decode('utf-8'), completetime.strftime(TIME2_FORMAT).decode('utf-8'))

def orderArrival(order):
    starttime = datetime.strptime(order['starttime'], DATETIME_FORMAT)
    return ORDER_ARRIVAL %(order['assistant_name'], starttime.strftime(DATE_FORMAT).decode('utf-8'), starttime.strftime(TIME_FORMAT).decode('utf-8'),
            datetime.strptime(order['endtime'], DATETIME_FORMAT).strftime(TIME_FORMAT).decode('utf-8'), order['poolroom_name'], order['payment'],
            order['user_nickname'], order['user_cellphone'])