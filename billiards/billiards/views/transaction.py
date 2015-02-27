# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2014年6月14日

@author: kane
'''
from alipay import Alipay, WapAlipay
from billiards.models import PayAccount, Transaction, Goods,\
    AssistantAppointment
from datetime import datetime, timedelta
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.utils.timezone import pytz, utc
from billiards.settings import TIME_ZONE
from billiards import settings
from django.shortcuts import get_object_or_404, redirect
import json
from mobi.decorators import detect_mobile
from urlparse import unquote
from xml.etree import ElementTree
from django.views.decorators.csrf import csrf_exempt
import logging
from billiards.commons import notification
from django.http.response import HttpResponseBadRequest

logger = logging.getLogger("transaction")

def getAlipay():
    account = PayAccount.objects.all()[:1][0]
    return (account, Alipay(pid=account.pid, key=account.key, seller_email=account.email))

def getWapAlipay():
    account = PayAccount.objects.all()[:1][0]
    return (account, WapAlipay(pid=account.pid, key=account.key, seller_email=account.email))

def getGoods(sku):
    return get_object_or_404(Goods, sku=sku)

PAYMENT_TIMEOUT = 15
def createTransaction(request, goods):
    isMobile = request.mobile
    account, alipay = getWapAlipay() if isMobile else getAlipay()
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
    returnurl = request.build_absolute_uri(reverse('transaction_alipay_wapreturn')) if isMobile else request.build_absolute_uri(reverse('transaction_alipay_return'))
    notifyurl = request.build_absolute_uri(reverse('transaction_alipay_wapnotify')) if isMobile else request.build_absolute_uri(reverse('transaction_alipay_notify'))
    if isMobile:
        params = {'out_trade_no': transaction.tradeNum,
              'subject': transaction.subject,
              'total_fee': transaction.fee,
              'seller_account_name': alipay.seller_email,
              'call_back_url': returnurl,
              'notify_url': notifyurl,
              'pay_expire': PAYMENT_TIMEOUT}
    else:
        params = {'out_trade_no': transaction.tradeNum, 'subject': transaction.subject, 'total_fee': transaction.fee, 
        'return_url': returnurl, 'notify_url': notifyurl, 'it_b_pay': '%sm' %(PAYMENT_TIMEOUT)}
    return (transaction, alipay.create_direct_pay_by_user_url(**params))

@detect_mobile
def alipay_goods(request, sku):
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

def alipay_wapreturn(request):
    account, alipay = getWapAlipay()
    parameters = {k: unquote(v) for k, v in request.GET.iteritems()}
    if alipay.verify_notify(**parameters):
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
        account, alipay = getWapAlipay()
        parameters = {k: v for k, v in request.POST.iteritems()}
        logger.info("Received alipay wap notify at %s with parameters '%s'." %(datetime.now(), 
            '&'.join(['%s=%s' % (key, v) for key,v in request.POST.iteritems()])))
        if alipay.verify_notify(**parameters):
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

def transactionSuccessNotification(transaction, isMobile = True):
    notification(u"%s订单%s支付完成" %(u'手机' if isMobile else '', transaction.tradeNum), u"%s - %s元" %(transaction.goods.name, transaction.fee))
    order = AssistantAppointment.objects.get(transaction=transaction)
    order.state = 2
    order.save()
    
def alipay_return(request):
    account, alipay = getAlipay()
    parameters = {k: v for k, v in request.GET.iteritems()}
    if alipay.verify_notify(**parameters):
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
        account, alipay = getAlipay()
        parameters = {k: v for k, v in request.POST.iteritems()}
        logger.info("Received alipay notify at %s with parameters '%s'." %(datetime.now(), 
            '&'.join(['%s=%s' % (key, v) for key,v in request.POST.iteritems()])))
        if alipay.verify_notify(**parameters):
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
