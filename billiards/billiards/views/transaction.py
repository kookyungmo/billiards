# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2014年6月14日

@author: kane
'''
from billiards.models import Transaction, Goods,\
    AssistantAppointment, PayAccount
from datetime import datetime, timedelta
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.timezone import pytz
from billiards import settings
from django.shortcuts import get_object_or_404, redirect
import json
from mobi.decorators import detect_mobile
import logging
from billiards.commons import notification, isWechatBrowser
from django.http.response import HttpResponseBadRequest
from billiards.pay import Pay

logger = logging.getLogger("transaction")

def getGoods(sku):
    return get_object_or_404(Goods, sku=sku)

def createTransaction(request, goods):
    isMobile = request.mobile
    if isWechatBrowser(request.META['HTTP_USER_AGENT']):
        paymethod = Pay.getPayMethod(PayAccount.Nowpay)
    else:
        paymethod = Pay.getPayMethod()
    account = paymethod.getAccount(isMobile)
    nativetime = datetime.utcnow()
    localtz = pytz.timezone(settings.TIME_ZONE)
    localtime = localtz.localize(nativetime)
    extendtime = localtime + timedelta(days=-15)
    transaction, created = Transaction.objects.get_or_create(payaccount=account, subject=goods.name, user=request.user, goods=goods, fee=goods.price, 
        state=1, createdDate__gt=extendtime, 
        defaults={'createdDate': datetime.utcnow(), 'payaccount': account, 'subject': goods.name, 'user': request.user,
                  'goods': goods, 'fee': goods.price, 'state': 1})
    if created == True:
        transaction.save()
        
    return (transaction, paymethod.getPayUrl(request, account, isMobile, transaction))

@detect_mobile
def pay_goods(request, sku):
    if request.user.is_authenticated():
        goods = getGoods(sku)
        transaction, url = createTransaction(request, goods)
        if goods.type == 2:
            try:
                aa = AssistantAppointment.objects.get(transaction=transaction)
                if aa.state != 1:
                    return redirect('user_assistant_order')
            except AssistantAppointment.DoesNotExist:
                raise HttpResponseBadRequest('illegal request')
        if transaction.paymentExpired:
            return redirect('user_assistant_order')
        return HttpResponseRedirect(url)
    return HttpResponse(json.dumps({'rt': -1, 'msg': 'login first'}), content_type="application/json")

TRANSACTION_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

def getIdFromTradeNum(tradenum):
    return int(tradenum[8:])

def transactionSuccessNotification(transaction, isMobile = True):
    notification(u"%s订单%s支付完成" %(u'手机' if isMobile else '', transaction.tradeNum), u"%s - %s元" %(transaction.goods.name, transaction.fee))
    order = AssistantAppointment.objects.get(transaction=transaction)
    order.state = 2
    order.save()
