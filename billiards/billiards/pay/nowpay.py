# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2015年3月2日

@author: kane
'''
import logging
from billiards.pay import Pay, Nowpay
from billiards.models import PayAccount, Transaction
import six
from billiards.views.transaction import getIdFromTradeNum,\
    transactionSuccessNotification
from datetime import datetime
from django.shortcuts import redirect
from django.http.response import HttpResponse
from django.utils.timezone import pytz, utc
from billiards.settings import TIME_ZONE
from django.views.decorators.csrf import csrf_exempt
if six.PY3:
    from urllib.parse import unquote, parse_qs
else:
    from urlparse import unquote, parse_qs

logger = logging.getLogger("transaction")

def pay_return(request):
    paymethod = Pay.getPayMethod(PayAccount.Nowpay)
    account = paymethod.getAccount(True)
    pay = Nowpay()
    parameters = {k: unquote(v) for k, v in request.GET.iteritems()}
    if parameters['appId'] == account.pid and parameters['signature'] ==\
        pay.doSign(parameters, ('signType', 'signature'), account.key):
        tradenum = request.GET.get('mhtOrderNo')
        try:
            transaction = Transaction.objects.get(id=getIdFromTradeNum(tradenum))
            if transaction.state != 2 and transaction.state != 5 and parameters['tradeStatus'] == 'A001':
                transaction.tradeStatus = 'TRADE_SUCCESS'
                transaction.paidDate = datetime.now().replace(tzinfo=utc).astimezone(pytz.timezone(TIME_ZONE))
                transaction.state = 2
                transaction.save()
                
                transactionSuccessNotification(transaction)
            
            #might add a page
            if transaction.goods.type == 2:
                return redirect('user_assistant_order')
            return HttpResponse("Payment completed.")
        except Transaction.DoesNotExist:
            #TODO handle error case
            pass
    return HttpResponse("Error.")

@csrf_exempt
def pay_notify(request):
    try:
        paymethod = Pay.getPayMethod(PayAccount.Nowpay)
        account = paymethod.getAccount(True)
        pay = Nowpay()
        parameters = {k: v for k, v in parse_qs(request.body)}
        logger.info("Received nowpay asynchronized notify at %s with parameters '%s'." %(datetime.now(), 
            '&'.join(['%s=%s' % (key, v) for key,v in parameters.iteritems()])))
        if parameters['appId'] == account.pid and parameters['signature'] ==\
            pay.doSign(parameters, ('signType', 'signature'), account.key):
            tradenum = parameters['mhtOrderNo']
            try:
                transaction = Transaction.objects.get(id=getIdFromTradeNum(tradenum))
                if transaction.tradeStatus == 'TRADE_FINISHED' or transaction.tradeStatus == 'TRADE_CLOSED':
                    # already completed transaction
                    return HttpResponse("success=Y")
                elif parameters['tradeStatus'] == 'A001':
                    if 'nowPayAccNo' in parameters:
                        transaction.paytradeNum = parameters['tradeStatus']
                    transaction.tradeStatus = 'TRADE_SUCCESS'
                    transaction.paidDate = datetime.now().replace(tzinfo=utc).astimezone(pytz.timezone(TIME_ZONE))
                    transaction.state = 2
                    transaction.save()
                
                    transactionSuccessNotification(transaction)
                    return HttpResponse("success=Y")
                logger.warn('Notify the transcation with error code %s.' %(parameters['tradeStatus']))
            except Transaction.DoesNotExist:
                #TODO handle error case
                pass
        else:
            logger.warn("nowpay notify is illegal.")
    except Exception:
        logger.exception("exception occurred when processing nowpay notification.")
    return HttpResponse("Error.")