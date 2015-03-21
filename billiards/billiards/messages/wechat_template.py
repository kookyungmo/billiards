# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2015年3月4日

@author: kane
'''
from django.core.urlresolvers import reverse
from billiards.settings import SITE_DOMAIN
from datetime import datetime
from billiards.models import DATETIME_FORMAT, Assistant, AssistantUser
from billiards.messages.assistant import DATE_FORMAT, TIME_FORMAT
from django.utils.timezone import localtime

MSG_TEMPLATE=u'''
            {
           "touser":"%s",
           "template_id":"%s",
           "url":"%s",
           "topcolor":"#FF0000",
           "data":{
                   %s
           }
       }'''
       
ORDER_PAY_SUCCESS=u'''
                   "first": {
                       "value":"【我为台球狂】我们已经收到您的订单，等待助教确认。",
                       "color":"#173177"
                   },
                   "orderMoneySum":{
                       "value":"%s元",
                       "color":"#173177"
                   },
                   "orderProductName": {
                       "value":"预约时间：%s，%s点-%s点；预约球房：%s；球房地址：%s",
                       "color":"#173177"
                   },
                   "remark":{
                       "value":"感谢您使用教练预约平台。请在【我为台球狂】微信公众平台—我的订单查看预约详情。",
                       "color":"#173177"
                   }
                   '''
ORDER_ARRIVAL=u'''
                "first": {
                       "value":"【我为台球狂】有您的一个预约订单。",
                       "color":"#173177"
                   },
                   "tradeDateTime":{
                       "value":"%s",
                       "color":"#173177"
                   },
                   "orderType":{
                       "value":"预约%s，%s点-%s点；消费金额：%s元",
                       "color":"#173177"
                   },
                   "customerInfo": {
                       "value":"客户昵称：%s；客户联系电话：%s",
                       "color":"#173177"
                   },
                   "orderItemName":{
                       "value":"预约球房：%s",
                       "color":"#173177"
                   },
                   "orderItemData":{
                       "value":"球房地址：%s",
                       "color":"#173177"
                   },
                   "remark":{
                       "value":"消费时，请向客户索要消费码，并发送给【我为台球狂】微信公众平台。",
                       "color":"#173177"
                   }
                '''
                   
ORDER_CONFIRMATION=u'''
                    "first": {
                       "value":"【我为台球狂】您的订单已确认，请您准时到场消费。",
                       "color":"#173177"
                   },
                   "keyword1":{
                       "value":"预约助教：%s；预约单价：%s元/小时；消费金额：%s元；",
                       "color":"#173177"
                   },
                   "keyword2":{
                       "value":"预约时间：%s，%s点-%s点；预约时长：%s小时",
                       "color":"#173177"
                   },
                   "keyword3": {
                       "value":"预约球房：%s；球房地址：%s",
                       "color":"#173177"
                   },
                   "remark":{
                       "value":"消费时，请将您的消费码告知助教。感谢您使用教练预约平台。请在【我为台球狂】微信公众平台—我的订单，查看预约详情。",
                       "color":"#173177"
                   }
                   '''
                   
ORDER_COMPLETE=u'''
                "first": {
                       "value":"【我为台球狂】您的订单已消费。",
                       "color":"#173177"
                   },
                   "Content1":{
                       "value":"您的助教预约服务已经完成",
                       "color":"#173177"
                   },
                   "Good":{
                       "value":"预约% 时间：%s，%s点-%s点；预约时长：%s小时",
                       "color":"#173177"
                   },
                   "contentType": {
                       "value":"预约球房：%s；球房地址：%s",
                       "color":"#173177"
                   },
                   "price": {
                       "value":"消费金额：%s元",
                       "color":"#173177"
                   },
                   "menu": {
                       "value":"预约单价：%s元/小时",
                       "color":"#173177"
                   },
                   "remark":{
                       "value":"感谢您使用教练预约平台。感谢您使用教练预约平台。请在【我为台球狂】微信公众平台—我的订单，查看预约详情。",
                       "color":"#173177"
                   }
                   '''

def buildURL(relativeURL):
    return "http://%s%s" %(SITE_DOMAIN, relativeURL)

def orderConfirmationMsg(order, user):
    starttime = datetime.strptime(order['starttime'], DATETIME_FORMAT)
    return MSG_TEMPLATE %(user.username, u'hvCxdrH9TCgxa7ygdJhmWwFcUk9fMLBzblZd4iFYLTs', buildURL(reverse('user_assistant_order')),
            ORDER_CONFIRMATION %(order['assistant_name'], order['price'], order['payment'],
                starttime.strftime(DATE_FORMAT).decode('utf-8'), starttime.strftime(TIME_FORMAT).decode('utf-8'),
                datetime.strptime(order['endtime'], DATETIME_FORMAT).strftime(TIME_FORMAT).decode('utf-8'), order['duration'],
                order['poolroom_name'], order['poolroom_address']))
    
def orderPaySuccess(order, user):
    starttime = datetime.strptime(order['starttime'], DATETIME_FORMAT)
    return MSG_TEMPLATE %(user.username, u'YFDD2KzlnMkotFsPPgE7krZ-C1fWGuSSK0Ao0NNqkKE', buildURL(reverse('user_assistant_order')),
            ORDER_PAY_SUCCESS %(order['payment'], starttime.strftime(DATE_FORMAT).decode('utf-8'), starttime.strftime(TIME_FORMAT).decode('utf-8'),
                datetime.strptime(order['endtime'], DATETIME_FORMAT).strftime(TIME_FORMAT).decode('utf-8'),
                order['poolroom_name'], order['poolroom_address']))
    
def orderComplete(order, user):
    starttime = datetime.strptime(order['starttime'], DATETIME_FORMAT)
    return MSG_TEMPLATE %(user.username, u'gJLPV2PQt6Ql5R58_Gl5_T5spwT7cvmzvQbprfVqHkY', buildURL(reverse('user_assistant_order')),
            ORDER_COMPLETE %(order['assistant_name'], starttime.strftime(DATE_FORMAT).decode('utf-8'), starttime.strftime(TIME_FORMAT).decode('utf-8'),
                datetime.strptime(order['endtime'], DATETIME_FORMAT).strftime(TIME_FORMAT).decode('utf-8'), order['duration'],
                order['poolroom_name'], order['poolroom_address'],
                order['payment'],
                order['price']))

def orderArrival(order, user):
    starttime = datetime.strptime(order['starttime'], DATETIME_FORMAT)
    try:
        assistant = Assistant.objects.get(uuid=order['assistant_id'])
        au = AssistantUser.objects.get(assistant=assistant)
        if au.user.site_name.startswith('wechat'):
            return MSG_TEMPLATE %(au.user.username, u'EiXPxXqBWkNTHqJYu3uTNoXvToSmp7PzvihPySGT4tU', buildURL(reverse('assistant_orders', args=(order['assistant_id']))),
            ORDER_ARRIVAL %(localtime(datetime.utcnow()).strftime(DATETIME_FORMAT).decode('utf-8'), 
                starttime.strftime(DATE_FORMAT).decode('utf-8'), starttime.strftime(TIME_FORMAT).decode('utf-8'), 
                datetime.strptime(order['endtime'], DATETIME_FORMAT).strftime(TIME_FORMAT).decode('utf-8'), order['payment'],
                order['user_nickname'], order['user_cellphone'],
                order['poolroom_name'], order['poolroom_address']))
        return None
    except Assistant.DoesNotExist or AssistantUser.DoesNotExist:
        return None