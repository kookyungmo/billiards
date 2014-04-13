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
from django.http import HttpResponse
from django.db.models.query_utils import Q
from billiards.models import Poolroom

class BJUniversityAssociationWechat(PKWechat):
    def __init__(self, token, request):
        super(BJUniversityAssociationWechat, self).__init__(token, request, 2)
        
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
        return u'欢迎您关注北京高校台球联盟微信。发送 ？，帮助，获取帮助手册。'
    
    def getHelpMesg(self):
        return u"发送'俱乐部'或'球房'查找高校台球联盟的合作球房。发送'活动'获取一周内高校台球联盟活动详情。"
    
    def text(self):
        def text_handler(message):
            if message.content == u"活动":
                acts = self.getActs(float(message.time))
                acts = acts.filter(Q(organizer=2))
                count = acts.count()
                if count > 0:
                    acts = acts[:MAX_NEWSITEM]
                    reply = self.getActsReply(acts)
                    recordUserActivity(message.source, 'text', 'activity', {'content': message.content}, message.time, 
                                       {'count': len(acts), 'activity': True}, self.target)
                else:
                    recordUserActivity(message.source, 'text', 'noactivity', {'content': message.content}, message.time, 
                                       None, self.target)
                    reply = u'最近7天内没有被收录的北京高校台球联盟活动'
            elif message.content == u"俱乐部" or message.content == u"球房":
                poolrooms = Poolroom.objects.filter(poolroomuser__group=2).order_by('?')[:10]
                if len(poolrooms) > 0:
                    reply = self.getNewsPoolroomsReply(poolrooms)
                    recordUserActivity(message.source, 'text', 'poolroom', {'content': message.content}, message.time, 
                                   {'count': len(poolrooms)}, self.target)
                else:
                    reply = u'暂时没有收录的北京高校台球联盟合作球房'
                    recordUserActivity(message.source, 'text', 'nopoolroom', {'content': message.content}, message.time, 
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

def response_msg_bj_dabenying():
    pass    

@csrf_exempt
def bj_dabenying(request):
    if request.method=='GET':
#         return HttpResponse(checkSignature(request, token='babenying@pktaiqiu'))
        pass
    elif request.method=='POST':
        return HttpResponse(response_msg_bj_dabenying(request),content_type="application/xml")