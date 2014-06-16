# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2014年6月14日

@author: kane
'''
from alipay import Alipay
from billiards.models import PayAccount, Transaction, Goods
from datetime import datetime, timedelta
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.utils.timezone import pytz
from billiards.settings import TIME_ZONE
from billiards import settings
from django.shortcuts import get_object_or_404

def getAlipay():
    account = PayAccount.objects.all()[:1][0]
    return (account, Alipay(pid=account.pid, key=account.key, seller_email=account.email))

def getGoods(sku):
    return get_object_or_404(Goods, sku=sku)

def alipay_goods(request, sku):
    if request.user.is_authenticated():
        goods = getGoods(sku)
        account, alipay = getAlipay()
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
        returnurl = request.build_absolute_uri(reverse('transaction_alipay_return'))
        notifyurl = request.build_absolute_uri(reverse('transaction_alipay_notify'))
        url = alipay.create_direct_pay_by_user_url(out_trade_no=transaction.tradenum, subject=transaction.subject, total_fee=transaction.fee, 
            return_url=returnurl, notify_url=notifyurl)
        return HttpResponseRedirect(url)
    return None

TRANSACTION_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
def alipay_return(request):
    account, alipay = getAlipay()
    parameters = {k: v for k, v in request.GET.iteritems()}
    if alipay.verify_notify(**parameters):
        if request.GET.get('is_success') == 'T':
            tradenum = request.GET.get('out_trade_no')
            try:
                transaction = Transaction.objects.get(tradenum=tradenum)
                transaction.paytradeNum = request.GET.get('trade_no')
                transaction.tradeStatus = request.GET.get('trade_status')
                transaction.notifyid = request.GET.get('notify_id')
                transaction.buyerEmail = request.GET.get('buyer_email')
                transaction.buyeid = request.GET.get('buyer_id')
                if transaction.tradeStatus == 'TRADE_FINISHED' or transaction.tradeStatus == 'TRADE_SUCCESS':
                    transaction.paidDate = datetime.strptime(request.GET.get('notify_time'), TRANSACTION_TIME_FORMAT).replace(tzinfo=pytz.timezone(TIME_ZONE))
                    transaction.state = 2
                transaction.save()
                return HttpResponse("Payment completed.")
            except Transaction.DoesNotExist:
                #TODO handle error case
                pass
    return HttpResponse("Error.")

def alipay_notify(request):
    account, alipay = getAlipay()
    if alipay.verify_notify(**request.GET):
        tradenum = request.GET.get('out_trade_no')
        try:
            transaction = Transaction.objects.get(tradenum=tradenum)
            if transaction.tradeStatus == 'TRADE_FINISHED' or transaction.tradeStatus == 'TRADE_CLOSED':
                # already completed transaction
                return
            if transaction.paytradeNum is None:
                transaction.paytradeNum = request.GET.get('trade_no')
            transaction.tradeStatus = request.GET.get('trade_status')
            transaction.notifyid = request.GET.get('notify_id')
            transaction.buyerEmail = request.GET.get('buyer_email')
            transaction.buyeid = request.GET.get('buyer_id')
            if transaction.tradeStatus == 'TRADE_FINISHED' or transaction.tradeStatus == 'TRADE_SUCCESS':
                transaction.paidDate = datetime.strptime(request.GET.get('gmt_payment'), TRANSACTION_TIME_FORMAT).replace(tzinfo=pytz.timezone(TIME_ZONE))
                transaction.state = 2
            elif transaction.tradeStatus == 'TRADE_CLOSED':
                transaction.closedDate = datetime.strptime(request.GET.get('gmt_close'), TRANSACTION_TIME_FORMAT).replace(tzinfo=pytz.timezone(TIME_ZONE))
                transaction.state = 4
            transaction.save()
            return HttpResponse("Received.")
        except Transaction.DoesNotExist:
            #TODO handle error case
            pass
    return HttpResponse("Error.")