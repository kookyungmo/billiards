# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2015年3月1日

@author: kane
'''
import six
from billiards.pay import Pay
import alipay
from billiards.views.transaction import getIdFromTradeNum,\
    transactionSuccessNotification, TRANSACTION_TIME_FORMAT
from xml.etree import ElementTree
if six.PY3:
    from urllib.parse import unquote
else:
    from urlparse import unquote
from billiards.models import Transaction
from datetime import datetime
import pytz
from billiards.settings import TIME_ZONE
from django.utils.timezone import utc
from django.shortcuts import redirect
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger("transaction")

def alipay_wapreturn(request):
    paymethod = Pay.getPayMethod()
    account = paymethod.getAccount(True)
    pay = alipay.WapAlipay(pid=account.pid, key=account.key, seller_email=account.email)
    parameters = {k: unquote(v) for k, v in request.GET.iteritems()}
    if pay.verify_notify(**parameters):
        tradenum = request.GET.get('out_trade_no')
        try:
            transaction = Transaction.objects.get(id=getIdFromTradeNum(tradenum))
            if transaction.state != 2 and transaction.state != 5:
                transaction.paytradeNum = request.GET.get('trade_no')
                transaction.tradeStatus = 'TRADE_SUCCESS'
                transaction.paidDate = datetime.now().replace(tzinfo=utc).astimezone(pytz.timezone(TIME_ZONE))
                transaction.state = 2
                transaction.save()
                
                transactionSuccessNotification(transaction)
        except Transaction.DoesNotExist:
            #TODO handle error case
            pass
        # add a page here
        if transaction.goods.type == 2:
            return redirect('user_assistant_order')
        return HttpResponse("Payment completed.")
    return HttpResponse("Error.")

@csrf_exempt
def alipay_wapnotify(request):
    try:
        paymethod = Pay.getPayMethod()
        account = paymethod.getAccount(True)
        pay = alipay.WapAlipay(pid=account.pid, key=account.key, seller_email=account.email)
        parameters = {k: v for k, v in request.POST.iteritems()}
        logger.info("Received alipay wap notify at %s with parameters '%s'." %(datetime.now(), 
            '&'.join(['%s=%s' % (key, v) for key,v in request.POST.iteritems()])))
        if pay.verify_notify(**parameters):
            tree = ElementTree.ElementTree(ElementTree.fromstring(unquote(parameters['notify_data']).encode("utf-8")))
            notifydata = {node.tag: node.text for node in tree.iter()}
            tradenum = notifydata['out_trade_no']
            try:
                transaction = Transaction.objects.get(id=getIdFromTradeNum(tradenum))
                if transaction.tradeStatus == 'TRADE_FINISHED' or transaction.tradeStatus == 'TRADE_CLOSED':
                    # already completed transaction
                    return HttpResponse("success")
                transaction.paytradeNum = notifydata['trade_no']
                transaction.tradeStatus = notifydata['trade_status']
                transaction.notifyid = notifydata['notify_id']
                transaction.buyeid = notifydata['buyer_id']
                transaction.paidDate = datetime.now().replace(tzinfo=utc).astimezone(pytz.timezone(TIME_ZONE)) if 'gmt_payment' not in notifydata else \
                    datetime.strptime(notifydata['gmt_payment'], TRANSACTION_TIME_FORMAT).replace(tzinfo=pytz.timezone(TIME_ZONE))
                transaction.state = 2 if notifydata['trade_status'] == 'TRADE_SUCCESS' else 5
                transaction.save()
                
                transactionSuccessNotification(transaction)
                return HttpResponse("success.")
            except Transaction.DoesNotExist:
                #TODO handle error case
                pass
        else:
            logger.warn("alipay wap notify is invalid.")
    except Exception:
        logger.exception("exception occurred when processing alipay wap notification.")
    return HttpResponse("Error.")

    
def alipay_return(request):
    paymethod = Pay.getPayMethod()
    account = paymethod.getAccount(True)
    pay = alipay.Alipay(pid=account.pid, key=account.key, seller_email=account.email)
    parameters = {k: v for k, v in request.GET.iteritems()}
    if pay.verify_notify(**parameters):
        if request.GET.get('is_success') == 'T':
            tradenum = request.GET.get('out_trade_no')
            try:
                transaction = Transaction.objects.get(id=getIdFromTradeNum(tradenum))
                if transaction.state != 2 and transaction.state != 5:
                    transaction.paytradeNum = request.GET.get('trade_no')
                    transaction.tradeStatus = request.GET.get('trade_status')
                    transaction.notifyid = request.GET.get('notify_id')
                    transaction.buyerEmail = request.GET.get('buyer_email')
                    transaction.buyeid = request.GET.get('buyer_id')
                    if transaction.tradeStatus == 'TRADE_FINISHED' or transaction.tradeStatus == 'TRADE_SUCCESS':
                        transaction.paidDate = datetime.strptime(request.GET.get('notify_time'), TRANSACTION_TIME_FORMAT).replace(tzinfo=pytz.timezone(TIME_ZONE))
                        transaction.state = 2
                    transaction.save()
                    
                    transactionSuccessNotification(transaction, False)
            except Transaction.DoesNotExist:
                #TODO handle error case
                pass
            # TODO add a page for it
            if transaction.goods.type == 2:
                return redirect('user_assistant_order')
            return HttpResponse("Payment completed.")
    return HttpResponse("Error.")

@csrf_exempt
def alipay_notify(request):
    try:
        paymethod = Pay.getPayMethod()
        account = paymethod.getAccount(True)
        pay = alipay.Alipay(pid=account.pid, key=account.key, seller_email=account.email)
        parameters = {k: v for k, v in request.POST.iteritems()}
        logger.info("Received alipay notify at %s with parameters '%s'." %(datetime.now(), 
            '&'.join(['%s=%s' % (key, v) for key,v in request.POST.iteritems()])))
        if pay.verify_notify(**parameters):
            tradenum = request.GET.get('out_trade_no')
            try:
                transaction = Transaction.objects.get(id=getIdFromTradeNum(tradenum))
                if transaction.tradeStatus == 'TRADE_FINISHED' or transaction.tradeStatus == 'TRADE_CLOSED':
                    # already completed transaction
                    return HttpResponse("success")
                if transaction.paytradeNum is None:
                    transaction.paytradeNum = request.GET.get('trade_no')
                transaction.tradeStatus = request.GET.get('trade_status')
                transaction.notifyid = request.GET.get('notify_id')
                transaction.buyerEmail = request.GET.get('buyer_email')
                transaction.buyeid = request.GET.get('buyer_id')
                if transaction.tradeStatus == 'TRADE_FINISHED' or transaction.tradeStatus == 'TRADE_SUCCESS':
                    transaction.paidDate = datetime.strptime(request.GET.get('gmt_payment'), TRANSACTION_TIME_FORMAT).replace(tzinfo=pytz.timezone(TIME_ZONE))
                    transaction.state = 2
                    transactionSuccessNotification(transaction, False)
                elif transaction.tradeStatus == 'TRADE_CLOSED':
                    transaction.closedDate = datetime.strptime(request.GET.get('gmt_close'), TRANSACTION_TIME_FORMAT).replace(tzinfo=pytz.timezone(TIME_ZONE))
                    transaction.state = 4
                transaction.save()
                return HttpResponse("success")
            except Transaction.DoesNotExist:
                #TODO handle error case
                pass
        else:
            logger.warn("alipay notify is invalid.")
    except Exception:
        logger.exception("exception occurred when processing alipay notification.")
    return HttpResponse("Error.")
