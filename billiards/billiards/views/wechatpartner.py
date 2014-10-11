# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2014年4月13日

@author: kane
'''
from django.views.decorators.csrf import csrf_exempt
from billiards.views.wechat import \
    recordUserActivity, \
    HELP_KEYWORDS, PKWechat, MAX_NEWSITEM
from django.db.models.query_utils import Q
from billiards.models import Poolroom, PoolroomUser
from billiards.location_convertor import gcj2bd
from billiards.views.poolroom import getNearbyPoolrooms
from datetime import datetime
from billiards.views.challenge import getNearbyChallenges

class BJUniversityAssociationWechat(PKWechat):
    def __init__(self, token, request):
        super(BJUniversityAssociationWechat, self).__init__(token, request, self.getOrgnizerId())
        
    def addHandlers(self):
        self.add_handler(self.subscribe(), 'subscribe')
        self.add_handler(self.unsubscribe(), 'unsubscribe')
        self.add_handler(self.text(), 'text')
        self.add_handler(self.help(), 'all')
        
    def getFromSoureStr(self):
        return 'wechat-bj-university'
        
    def getSpecialEventItem(self, receivedtime):
        return ''
        
    def getWelcomeMsg(self):
        return u'欢迎您关注%s微信公众号。发送 ？，帮助，获取帮助手册。' %(self.getGroupName())
    
    def getHelpMesg(self):
        return u"发送'俱乐部'或'球房'查找%s的合作球房。发送'活动'获取一周内%s活动详情。" %(self.getGroupName(), self.getGroupName())
    
    def getOrgnizerId(self):
        return 2
    
    def getGroupName(self):
        return u'北京高校台球联盟'
    
    def text(self):
        def text_handler(message):
            if message.content == u"活动":
                acts = self.getActs(float(message.time))
                acts = acts.filter(Q(organizer=self.getOrgnizerId()))
                count = acts.count()
                if count > 0:
                    acts = acts[:MAX_NEWSITEM]
                    reply = self.getActsReply(acts)
                    recordUserActivity(message, 'text', 'activity', {'content': message.content}, 
                                       {'count': len(acts), 'activity': True}, self.target)
                else:
                    recordUserActivity(message, 'text', 'noactivity', {'content': message.content},
                                       None, self.target)
                    reply = u'最近7天内没有被收录的%s活动' %(self.getGroupName())
            elif message.content == u"俱乐部" or message.content == u"球房":
                poolrooms = Poolroom.objects.filter(poolroomuser__group=self.getOrgnizerId()).order_by('?')[:10]
                if len(poolrooms) > 0:
                    reply = self.getNewsPoolroomsReply(poolrooms)
                    recordUserActivity(message, 'text', 'poolroom', {'content': message.content},
                                   {'count': len(poolrooms)}, self.target)
                else:
                    reply = u'暂时没有收录的%s合作球房' %(self.getGroupName())
                    recordUserActivity(message, 'text', 'nopoolroom', {'content': message.content},
                                   None, self.target)
            elif message.content in HELP_KEYWORDS:
                reply = self.getHelpMesg()
            else:
                reply = u'%s%s' %(u'感谢您发送的消息。', self.getHelpMesg())
            return reply
        return text_handler
        
@csrf_exempt
def bj_university_association(request):
    robot = BJUniversityAssociationWechat("pktaiqiucom", request)
    if request.method=='GET':
        return robot.echo(request)
    elif request.method=='POST':
        return robot.handle(request)

class BJDaBengYingWechat(BJUniversityAssociationWechat):
    def addHandlers(self):
        self.add_handler(self.subscribe(), 'subscribe')
        self.add_handler(self.unsubscribe(), 'unsubscribe')
        self.add_handler(self.text(), 'text')
        self.add_handler(self.location(), 'location')
        self.add_handler(self.help(), 'all')
        
    def getFromSoureStr(self):
        return 'wechat-bj-dabengying'

    def getGroupName(self):
        return u'北京台球大本营'
        
    def getHelpMesg(self):
        return u"发送'位置'信息获取合作球房，群内一周内活动以及抢台费信息。发送'俱乐部'或'球房'查找北京台球大本营的合作球房。发送'活动'获取一周内台球大本营活动详情。"
    
    def getOrgnizerId(self):
        return 4
    
    def location(self):
        def location_handler(message):
            reply = []
            
            lat = message.location[0]
            lng = message.location[1]
            baidu_loc = gcj2bd(float(lat),float(lng))
            baidu_loc_lat = unicode(baidu_loc[0])
            baidu_loc_lng = unicode(baidu_loc[1])
            
            challengeReply = self.getChallengeReply(message, baidu_loc_lat, baidu_loc_lng)
            
            acts = self.getActs(float(message.time))
            acts = acts.filter(Q(organizer=self.getOrgnizerId()))
            count = acts.count()
            if count > 0:
                acts = acts[:MAX_NEWSITEM - len(challengeReply)]
                reply += self.getActsReply(acts)
            
            nearbyChallenges = getNearbyChallenges(lat, lng, 5, datetime.utcfromtimestamp(float(message.time)), self.getOrgnizerId())[:MAX_NEWSITEM - len(reply) - len(challengeReply)]
            nearbyCount = len(nearbyChallenges)
            
            poolrooms = PoolroomUser.objects.filter(Q(group=self.getOrgnizerId()))
            if poolrooms.count() > 0:
                ids = ','.join([str(pu.poolroom.id) for pu in poolrooms])
                nearbyPoolrooms = getNearbyPoolrooms(baidu_loc_lat, baidu_loc_lng, None, "poolroom.id in (%s)" %(ids))[:MAX_NEWSITEM - len(reply) - len(challengeReply)]
                if len(nearbyPoolrooms) + len(reply) + len(challengeReply) + nearbyCount > MAX_NEWSITEM:
                    nearbyPoolrooms = nearbyPoolrooms[:(1 if MAX_NEWSITEM - nearbyCount - len(reply) - len(challengeReply) <= 0 else MAX_NEWSITEM - nearbyCount - len(reply) - len(challengeReply))]
                    nearbyCount = nearbyCount[:MAX_NEWSITEM - len(reply) - len(challengeReply) - len(nearbyPoolrooms)]
                
                name, ids, distance = ([] for i in range(3))
                for poolroom in nearbyPoolrooms:
                    name.append(poolroom.name) 
                    ids.append(str(poolroom.id)) 
                    distance.append(str(poolroom.location_distance.km))
                rt = [','.join(fieldarray) for fieldarray in [name, ids, distance]]
                recordUserActivity(message, 'location', rt[0], {'lat': lat, 'lng': lng, 'scale': message.scale, 'label': ['Label']}, 
                                   {'id': rt[1], 'name': rt[0], 'distance': rt[2]}, self.target)
            else:
                nearbyChallenges = nearbyChallenges[:MAX_NEWSITEM - len(reply) - len(challengeReply)]
                nearbyPoolrooms = []
                
            reply = self.getNewsPoolroomsReply(nearbyPoolrooms) + reply
            reply.append(challengeReply[0])
            reply += self.getNearbyChallengeReply(nearbyChallenges)
            reply.append(challengeReply[1])
            return reply
        return location_handler

    def text(self):
        o_handler = super(BJDaBengYingWechat, self).text()
        def text_handler(message):
            if message.content == u'申请会员卡':
                return self.applyMember((), message, self.getOrgnizerId())
            elif message.content == u'查看会员卡':
                return self.queryMember((), message, self.getOrgnizerId())
            return o_handler(message)
        return text_handler
    
@csrf_exempt
def bj_dabenying(request):
    robot = BJDaBengYingWechat("babenying2pktaiqiu", request)
    if request.method=='GET':
        return robot.echo(request)
    elif request.method=='POST':
        return robot.handle(request)
