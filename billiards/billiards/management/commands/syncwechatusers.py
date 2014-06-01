# -*- coding: utf-8 -*-
# encoding: utf-8
'''
@author: kane
A utility tool to synchronize WeChat subscriber's information
'''
from django.core.management.base import NoArgsCommand
from billiards.models import WechatCredential
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from billiards.id import generator
from django.utils.timezone import utc
'''
For a known issue #48 of WeRobot to copy the client as workaround
'''
from billiards.client import Client
# from werobot.client import Client

class Command(NoArgsCommand):
    help = 'Synchronize WeChat subscriber\'s information'
    
    def isExpired(self, current, expiretime):
        return current.replace(tzinfo=utc) - expiretime.replace(tzinfo=utc) > timedelta(seconds = 5)
    
    def handle(self, *args, **options):
        creds = WechatCredential.objects.all()
        for cred in creds:
            self.stdout.write('Processing the subscriber of wechat account \'%s\'.\n' %(cred.name))
            
            client = Client(cred.appid, cred.secret)
            response = client.get_followers(None)
            
            if 'errcode' in response:
                self.stdout.write('Failed to process the subscriber of wechat account \'%s\' due to \'%s\'.\n' %(cred.name, response['errmsg']))
            else:
                self.stdout.write('\t\tTotally %s subscribers of wechat account \'%s\'.\n' %(response['total'], cred.name))
                
            CREATED = UPDATED = 0
            current = datetime.utcnow()
            expiretime = datetime.utcnow().replace(tzinfo=utc) + relativedelta(days=7)
            for openid in response['data']['openid']:
                idresponse = client.get_user_info(openid)
                if 'errorcode' in idresponse:
                    self.stdout.write('\t\t\t\tFailed to get info of subscriber \'%s\' of wechat account \'%s\' due to %s.\n' %(openid, cred.name, idresponse['errmsg']))
                elif int(idresponse['subscribe']) == 1:
                    obj, created = User.objects.get_or_create(username=idresponse['openid'],
                        defaults={'is_staff': 0, 'is_active': 1, 'is_superuser': 0, 
                                'date_joined': datetime.fromtimestamp(idresponse['subscribe_time']).replace(tzinfo=utc),
                                'nickname': idresponse['nickname'].encode('unicode_escape'), 'avatar': idresponse['headimgurl'], 
                                'gender': (lambda x: 'm' if x == 1 else 'f' if x == 2 else 'u')(int(idresponse['sex'])), 
                                'site_name': 'wechat/' + cred.name,
                                'password': 'wechat/%s:%s' %(cred.name, generator()),
                                'expire_time': expiretime})
                    if created == True:
                        CREATED += 1
                    elif obj != None and self.isExpired(current, obj.expire_time) \
                        and (obj.nickname != idresponse['nickname'].encode('unicode_escape') or obj.avatar != idresponse['headimgurl'] or \
                             obj.gender != (lambda x: 'm' if x == 1 else 'f' if x == 2 else 'u')(int(idresponse['sex']))):
                        obj.gender = (lambda x: 'm' if x == 1 else 'f' if x == 2 else 'u')(int(idresponse['sex']))
                        obj.nickname = idresponse['nickname'].encode('unicode_escape')
                        obj.avatar = idresponse['headimgurl']
                        obj.save()
                        UPDATED += 1
            self.stdout.write('\t\t %s subscribers are created, %s subscribers are updated for wechat account \'%s\'.\n' %(CREATED, UPDATED, cred.name))
            self.stdout.write('Completed processing the subscriber of wechat account \'%s\'.\n' %(cred.name))
                            