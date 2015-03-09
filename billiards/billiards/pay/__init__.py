# -*- coding: utf-8 -*-
# encoding: utf-8
from billiards.models import PayAccount
from django.utils import importlib
from django.core.urlresolvers import reverse
import logging
from billiards.commons import getClass
from hashlib import md5
import alipay

logger = logging.getLogger("transaction")

class Pay(object):
    PAYMENT_TIMEOUT = 15
    
    @staticmethod
    def getPayMethod(method = PayAccount.Alipay):
        try:
            method = next(name for value, name in PayAccount.TYPES
                      if value==method)
            return getClass('billiards.pay.%s' %(method))()
        except StopIteration:
            return None
        
    def getPayUrl(self, request, account, isMobile, transaction):
        pass
    
    def getAccount(self):
        pass
    
class Alipay(Pay):
    def getPayUrl(self, request, account, isMobile, transaction):
        pay = alipay.WapAlipay(pid=account.pid, key=account.key, seller_email=account.email) if isMobile else alipay.Alipay(pid=account.pid, key=account.key, seller_email=account.email)
        returnurl = request.build_absolute_uri(reverse('transaction_alipay_wapreturn')) if isMobile else request.build_absolute_uri(reverse('transaction_alipay_return'))
        notifyurl = request.build_absolute_uri(reverse('transaction_alipay_wapnotify')) if isMobile else request.build_absolute_uri(reverse('transaction_alipay_notify'))
        if isMobile:
            params = {'out_trade_no': transaction.tradeNum,
                  'subject': transaction.subject,
                  'total_fee': transaction.fee,
                  'seller_account_name': pay.seller_email,
                  'call_back_url': returnurl,
                  'notify_url': notifyurl,
                  'pay_expire': self.PAYMENT_TIMEOUT}
        else:
            params = {'out_trade_no': transaction.tradeNum, 'subject': transaction.subject, 'total_fee': transaction.fee, 
            'return_url': returnurl, 'notify_url': notifyurl, 'it_b_pay': '%sm' %(self.PAYMENT_TIMEOUT)}
        return pay.create_direct_pay_by_user_url(**params)

    def getAccount(self, isMobile = True):
        return PayAccount.objects.filter(type=PayAccount.Alipay)[:1][0]
    
class Nowpay(Pay):
    def getAccount(self, isMobile = True):
        return PayAccount.objects.get(type=PayAccount.Nowpay)
    
    def doSign(self, mydict, execludeKeys, secret):
        toBeSigned = ''
        for key, value in sorted(mydict.iteritems()):
            if key not in execludeKeys and value != '':
                toBeSigned = '%s%s=%s&' %(toBeSigned, key, mydict[key])
        
        toBeSigned = toBeSigned + md5(secret.encode('utf-8')).hexdigest()
        
        return md5(toBeSigned.encode('utf-8')).hexdigest()
    
    def getPayUrl(self, request, account, isMobile, transaction):
        args = {'funcode': 'WP001', 'appId': account.pid, 'mhtOrderNo': transaction.tradeNum, 'mhtOrderName': transaction.subject[:40],
                'mhtOrderType': '01', 'mhtCurrencyType': '156', 'mhtOrderAmt': int(transaction.fee)*100, 'mhtOrderDetail': transaction.subject[:200],
                'mhtOrderTimeOut': str(self.PAYMENT_TIMEOUT * 60), 'mhtOrderStartTime': transaction.createdDate.strftime('%Y%m%d%H%M%S'),
                'notifyUrl': request.build_absolute_uri(reverse('transaction_nowpay_notify')), 'frontNotifyUrl': request.build_absolute_uri(reverse('transaction_nowpay_return')),
                'mhtCharset': 'UTF-8', 'deviceType': '06', 'payChannelType': '', 'consumerId': transaction.user.username,
                'consumerName': transaction.user.nickname, 'mhtSignType': 'MD5'}
        md5Sign = self.doSign(args, ('funcode', 'deviceType', 'mhtSignType', 'mhtSignature'), account.key)
        args['mhtSignature'] = md5Sign
        queryString = '&'.join(['%s=%s' % (key, value) for key, value in args.items()])
        return 'https://api.ipaynow.cn/?%s' %(queryString)
