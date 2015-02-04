# coding=utf-8
from StringIO import StringIO
from datetime import datetime, timedelta
from random import randint
import re

from dateutil.relativedelta import relativedelta
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils import simplejson, timezone
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
import pytz
from werobot.messages import TextMessage, EventMessage
from werobot.parser import parse_user_msg
from werobot.reply import create_reply, WeChatReply
from werobot.robot import BaseRoBot
from werobot.utils import to_text

from billiards import settings
from billiards.commons import set_query_parameter, KEY_PREFIX,\
    DisplayNameJsonSerializer, notification
from billiards.location_convertor import gcj2bd
from billiards.models import Coupon, getCouponCriteria, Poolroom, \
    WechatActivity, Event, Membership, Group, \
    getThumbnailPath, AssistantUser, AssistantOffer
from billiards.settings import TEMPLATE_ROOT, TIME_ZONE, SITE_LOGO_URL,\
    SITE_DOMAIN
from billiards.views.challenge import getNearbyChallenges
from billiards.views.match import getMatchByRequest
from billiards.views.poolroom import getNearbyPoolrooms
from django.contrib.auth.models import User
from billiards.views.assistant import ASSISTANT_OFFER_FILTER, getAssistantOffers

HELP_TITLE = u'"二月特惠来袭，打球也要有逼格'

def set_video():
    videos = [
              {"title":"毒液花式台球史诗级巨制！神一般的弗洛里安·科勒(Florian Kohler)", "plink":"http://billiardsalbum.bcs.duapp.com/2014/02/FlorianKohler1.jpg","description":"绝对不能错过的精彩！点击观看","vlink":"http://v.youku.com/v_show/id_XNTU3MjMyNjI0.html"},
              {"title":"花式台球帝-毒液和他的彪悍女友 未来最疯狂的特技球家庭！", "plink":"http://billiardsalbum.bcs.duapp.com/2014/02/FlorianKohler1.jpg","description":"精彩不容错过！点击观看","vlink":"http://v.youku.com/v_show/id_XNTIxMjQzMzM2.html"},
              {"title":"毒液 最新花式台球集锦", "plink":"http://billiardsalbum.bcs.duapp.com/2014/02/FlorianKohler1.jpg","description":"精彩！犀利！点击观看","vlink":"http://v.youku.com/v_show/id_XNDQyNzI5MjEy.html"},
              {"title":"牛人和美女台球桌上玩花式台球", "plink":"http://billiardsalbum.bcs.duapp.com/2014/02/FlorianKohler1.jpg", "description":"点击观看\r\n时长：02:58", "vlink":"http://v.qq.com/boke/page/w/0/y/w0125gr8cny.html"},
              {"title":"花式台球 最美的境界 Venom Trickshots", "plink":"http://billiardsalbum.bcs.duapp.com/2014/02/FlorianKohler1.jpg","description":"精彩！高清！点击观看","vlink":"http://v.youku.com/v_show/id_XMzExMjIxMDgw.html"}
              ]
    return videos
  
def set_zsbq_video():
    videos = [
              {"title":"2013年首届中式八球大师邀请赛决赛 加雷斯·波茨vs克里斯·梅林", "plink":"http://billiardsalbum.bcs.duapp.com/2014/02/potts.jpg","description":"加雷斯·波茨vs克里斯·梅林 点击观看\r\n时长：93:47","vlink":"http://v.youku.com/v_show/id_XNDk4Nzc2OTg4.html"},
              {"title":"加雷斯·波茨——清台集锦", "plink":"http://billiardsalbum.bcs.duapp.com/2014/02/potts.jpg","description":"点击观看\r\n时长：57:20","vlink":"http://v.youku.com/v_show/id_XNjA4Njg4OTQ0.html"},
              {"title":"李赫文VS亨德利01-“英伦汽车·乔氏杯”亨德利中式八球挑战赛", "plink":"http://billiardsalbum.bcs.duapp.com/2014/02/hendry.jpg","description":"点击观看\r\n时长：82:46","vlink":"http://v.youku.com/v_show/id_XMzgzOTg2MjIw.html"}
              ]
    return videos

def set_pic():
    pics = ["NI5B4DBUP_ZihYXxcnmztzOPohOE9e4OThm3UPLc3nZJFfg7MGWyBd43D2wi4UCe",
            "GyKwjOnao9S0wLmrXJn6UjdHC4mnK-YRufy-IKJ23GnOIdg5XQZULN3KQ_fjK2se",
            "ybHUAJZXq1yjbgtT5fi-c0h5TZVGhnsMX9iyQZ0Tw7DCDzfN9kiGsDbJRX92e44w",
            "syVNC2pWzdPNS46pybv4XvcHtCuDsdexGWZLeyZKW3NoQ_ZXcX1rbzgsuZ3IljS7",
            "Xi5pEU9b3irwrRu-7HAwzN8CQy_MWIW01_XMmVrcjBJFw0dEDWs2d1MgrFP7uDJN",
            "2Ib4l8bne06Zze1ifJXDHqJZiIDBC0jTC1mcnBx6LZamskvRQNohu-JVmDL38GM5",
            "IARm4EO8tF0cSmxWSx2hMiFPMRX7VVOIjINUTuvH3Kcd3CwSKamuZZkI2_2B2Xkw",
            "tIEBJVt7_3BVM8ynJV7CvVFYgIL5VxTcAM6MywZ4j02yGQwzqdoI__3MhXLn-NKK",
            "PgRUIcJGvYKwds5nHBrpuui_609w5JKM-23hMVJ6k6DBVJes088j7wXokR9J0war",
            "ecl1Fmh_zB0DaC2FA_8HC5q8pkWMSP27lk5xXgyExRdG-A_fqA-9LyYcyJuNNKNR",
            "jNcesbmUDJnzWpAr8wr6OhmQ2sQbUqc_bgqIF4WKF_TQWINi9wyDmpKwvzpoD-Nz",
            "TjUCyHdQDiYN8CjoJVm541kqpkMJXNlWKkPFNDzDfSWoZReynNHzkWhCVxH4rCqw",
            "gBLzJCrY_5Gk8wQkz7fYyWSa8dv5DWTEDjmyA1XY-YTW4J2d_NqulSBzis836Ffe",
            "tJB36nEeCbFaXF0AMk4t7L5YubKPzeyL5vQmI8qfM-JI6EfIe_o3Qaq4sDBCT6ne",
            "VQh8Ix7Tj9-5cIMkhg8G94sNACohza8q3xKe-kCMIYTlmmPK0ltRUXwcTaGdWj7l",
            "66wI6vj4y9QLzAYpSdg7qALuQxTd2-Do5D-wV3I13_hYqQhvXdHJEomRf4o98kOw",
            "EoqWm4TnVhR7KnZZaMfmwFoy3sgtfd2OL4L_lqcduHaOgr7jEvzB7HVEOOuDP6f5",
            "CN9f4evPHpz7k8J57FqwuDCLwWs-E5modvJXMPt6JU2iiTEnURJMC2995uHlGPHz",
            "V_knyD0qZpELQRAH_SpyEETTPiZwtnZkFqBETggd6l8d4u4KKT65KSLf_wX4DTMe",
            "2e0zTWKJScab6BEGWV6-MKicrl-d3rAjj351zpMVdPS6db9pu6sinkHqjeFcYUJz",
            "GJUBVTcraWK_yMynYlHPtUnGWxliIWlXEBwZJJELRI-Np2-CWKXFvIUurFYsf3O7"]
    return pics
  
def set_content():
    content = {
      #English content
      "hi":"Hello",
      "fj":"您想找附近的台球俱乐部吗？",
      "bs":"您想找台球俱乐部举办的比赛吗？",
      "nh":"你好啊，朋友",
      "bz":"帮助信息",
      "zf":"送祝福啦，祝您马年吉祥，身体健康，马到成功，财源滚滚来！",
      "yeah":"oh,yeah,我们一起为您欢呼",

      #Chinese content
      u"你好":"你好啊，朋友",
      u"早上好":"给您请早儿了",
      u"吃了吗":"劳您费心了，我吃了",
      u"新年好":"新年好呀，新年好呀，祝您和家人新年好，身体健康，万事如意",
      u"呵呵":"笑一笑十年少",
      u"再见":"您走好，欢迎随时找我来聊聊",
      u"我想回家":"走啊走啊走……到家了",
      u"徐浩":"他现在不在，稍后联系您",
      u"过节好":"您也过节好啊！",
      u"二":"不二不二",
      u"你二":"我不二啊",
      u"哈哈":"祝您每天都开心",
      u"改天":"择日不如撞日，今天就是良辰吉日",
      u"哥就是个传奇":"我们尊称您一声：传奇哥",
      u"你很帅":"您最帅了",
      u"我美吗":"您是我见过的世界上最美丽的容颜！",
      u"好玩":"好玩您就多玩会儿吧",
      u"新春快乐":"祝您马年马到成功，吉祥如意，吉星高照，大吉大利",
}
    return content
  
CLUB_NAMES = {'22': (u'北京慧聚台球俱乐部', u'慧聚台球', u'慧聚', u'慧聚台球俱乐部')}
HELP_KEYWORDS = (u"帮助", u"?", u"？", u'help')

LOGO_IMG_URL = SITE_LOGO_URL

MAX_NEWSITEM = 10

def shouldNotifyEvent(message, event, mapping):
    if event in mapping:
        if isinstance(mapping, dict):
            dictValue = mapping[event]
            if isinstance(dictValue, dict):
                for key, value in dictValue.iteritems():
                    if hasattr(message, key):
                        return shouldNotifyEvent(message, getattr(message, key), value)
            else:
                return True
        return True
    return False
    

def recordUserActivity(rawmessage, event, keyword, message, reply, target = 1):
    userid = rawmessage.source
    receivedtime = rawmessage.time
    nativetime = datetime.utcfromtimestamp(float(receivedtime))
    localtz = pytz.timezone(settings.TIME_ZONE)
    localtime = nativetime.replace(tzinfo=timezone.utc).astimezone(tz=localtz)
    newactivity = WechatActivity.objects.create_activity(userid, event, keyword, simplejson.dumps(message).decode('unicode-escape'), localtime, None if reply == None else simplejson.dumps(reply).decode('unicode-escape'), target)
    if event in settings.WECHAT_ACTIVITY_TRACE:
        newactivity.save()
        
    if  not settings.TESTING and (shouldNotifyEvent(rawmessage, event, settings.WECHAT_ACTIVITY_NOTIFICATION) or (keyword and keyword in settings.WECHAT_ACTIVITY_NOTIFICATION_KEYWORDS)):
        notification(u'New wechat activity -- %s' %(localtime), 
             u'[%s][%s] The "%s" message %s from "%s" was received at %s.' %(newactivity.get_target_display(), event, keyword, simplejson.dumps(message).decode('unicode-escape'), userid, localtime))
       
def buildPoolroomImageURL(poolroom):
    if poolroom.images.count() > 0:
        coverimage = poolroom.images.filter(iscover=1)
        if len(coverimage) > 0:
            return "%s%s" %(settings.MEDIA_URL[:-1], getThumbnailPath(coverimage[0].imagepath.name, 300))
        return "%s%s" %(settings.MEDIA_URL[:-1], getThumbnailPath(poolroom.images[:1][0].imagepath.name, 300))
    lng_baidu = str(poolroom.lng_baidu)
    lat_baidu = str(poolroom.lat_baidu)
    return "http://api.map.baidu.com/staticimage?center=%s,%s&width=450&height=300&zoom=18&scale=2&markers=%s,%s&markerStyles=-1,http://billiardsalbum.bcs.duapp.com/2014/01/marker-2.png" %(lng_baidu, lat_baidu, lng_baidu, lat_baidu)
            
def getNativeTime(utctime):
    localtz = pytz.timezone(settings.TIME_ZONE)
    return utctime.astimezone(localtz)

class ImageReply(WeChatReply):
    TEMPLATE = to_text("""
    <xml>
    <ToUserName><![CDATA[{target}]]></ToUserName>
    <FromUserName><![CDATA[{source}]]></FromUserName>
    <CreateTime>{time}</CreateTime>
    <MsgType><![CDATA[image]]></MsgType>
    <Image>
    <MediaId><![CDATA[{media_id}]]></MediaId>
    </Image>
    </xml>
    """)
    def render(self):
        return ImageReply.TEMPLATE.format(**self._args)

class DummyReply(WeChatReply):
    TEMPLATE = to_text('')

    def render(self):
        return DummyReply.TEMPLATE.format(**self._args)

class PKWechat(BaseRoBot):
    def __init__(self, token, request, target = 1):
        super(PKWechat, self).__init__(token, enable_session=False)
        self.request = request
        self.target = target
        self.addHandlers()
        
    def mapKeyHanlders(self):
        keyHandlers = {
            "PK_COUPON": self.getPKCoupon,
            "PK_ACTIVITY": self.getPKActivity,
            "PK_MATCH": self.getPKMatch,
            "PK_POOLROOM_NEARBY": self.getPKPoolroomNearby,
            "PK_ASSISTANT_RECOMMEND": self.getPKAssistantRecommend,
        }
        self.keysHandlers = keyHandlers
        self.add_handler(self.click(), "click")
        
    def click(self):
        def click_handler(message):
            reply = self.getSpecialEventItem(message.time)
            if message.key in self.keysHandlers:
                return self.keysHandlers[message.key](reply, message, 'event')
            reply += self.getHelpMesg()
            recordUserActivity(message, 'event', message.type, {'event': message.type, 'eventkey': message.key}, 
                    None, self.target)
            return reply    
        return click_handler
        
    def addHandlers(self):
        self._handlers['scan'] = []
        self.add_handler(self.subscribe(), 'subscribe')
        self.add_handler(self.scan(), 'scan')
        self.add_handler(self.unsubscribe(), 'unsubscribe')
        self.add_handler(self.location(), 'location')
        self.add_handler(self.userlocation(), 'location')
        self.add_handler(self.text(), 'text')
        self.add_handler(self.pic(), 'image')
        self.add_handler(self.help(), 'all')
        self.mapKeyHanlders()
        
    def hasSpecialEvent(self, receivedtime):
        nativetime = datetime.utcfromtimestamp(float(receivedtime))
        localtz = pytz.timezone(settings.TIME_ZONE)
        localtime = localtz.localize(nativetime)
        extendtime = localtime + timedelta(days=3)
        events = Event.objects.filter(((Q(startdate__gte=localtime) & Q(startdate__lte=extendtime)) | Q(startdate__lte=extendtime)) & Q(enddate__gt=localtime))
        if events.count() > 0:
            return events
        return None
    
    def getFromSoureStr(self):
        return 'wechat'
    
    def getActsReply(self, acts):
        reply = []
        for act in acts:
            picurl = buildPoolroomImageURL(act.poolroom)
            reply.append((act.title, u"活动开始时间: %s" %(getNativeTime(act.starttime)), picurl, self.buildAbsoluteURI(reverse('activity_detail', args=(act.pk,)))))
        return reply
    
    def getMatchesReply(self, matches):
        reply = []
        for match in matches:
            picurl = buildPoolroomImageURL(match.poolroom)
            reply.append((match.title, u"比赛开始时间: %s" %(getNativeTime(match.starttime)), picurl, self.buildAbsoluteURI(reverse('match_detail', args=(match.pk,)))))
        return reply

    def getNewsPoolroomsReply(self, poolrooms):
        reply = []
        for poolroom in poolrooms:
            address = poolroom.address
            tel = poolroom.tel
            size = str(poolroom.size)
            pkid = unicode(poolroom.pk)
            businesshours = poolroom.businesshours
            picurl = buildPoolroomImageURL(poolroom)
            originContent = self.buildAbsoluteURI(reverse('poolroom_detail_uuid', args=(poolroom.uuid,)))
            description = u"地址：%s\r\n营业面积：%s平方米\r\n营业时间：%s\r\n电话：%s" %(address, size, businesshours, tel)
            reply.append((poolroom.name, description, picurl, originContent))
        return reply
    
    def getChallengeReply(self, message, lat, lng):
        publishlink = set_query_parameter(self.buildAbsoluteURI(reverse('challenge_publish', args=(self.target, lat, lng, 3,))), 'uid', message.source)
        challlengelink = self.buildAbsoluteURI(reverse('challenge_with_distance', args=(self.target, lat, lng,)))
        reply = []
        reply.append((u"我要找人抢台费", u"找球打，新玩法--抢台费", LOGO_IMG_URL, publishlink))
        reply.append((u"看看别人的抢台费", u"查看已有的约球信息", LOGO_IMG_URL, challlengelink))
        return reply
    
    def getNearbyChallengeReply(self, nearbyChallenges):
        reply = []
        for challenge in nearbyChallenges:
            challlengelink = self.buildAbsoluteURI(reverse('challenge_detail', args=(challenge.id,)))
            loc = None
            if challenge.location is not None:
                locs = challenge.location.split(':')
                if len(locs) > 1:
                    loc = locs[1]
                else:
                    loc = u'球友目前所在的位置'
            else:
                loc = challenge.poolroom.name
            reply.append(((u"%s发起距离你%s公里的抢台费" %(challenge.issuer_nickname, "{0:.2f}".format(challenge.geolocation_distance.km))), u"抢台费的地点: %s" %(loc), LOGO_IMG_URL, challlengelink))
        return reply
    
    def getCouponsReply(self, coupons, withPoolroom = False):
        reply = []
        for coupon in coupons:
            picurl = buildPoolroomImageURL(coupon.poolroom)
            couponurl = self.buildAbsoluteURI(reverse('coupontracker', args=(coupon.id,)))
            reply.append((coupon.title, coupon.description, picurl, couponurl))
            if withPoolroom:
                picurl = buildPoolroomImageURL(coupon.poolroom)
                weblink = self.buildAbsoluteURI(reverse('poolroom_detail_uuid', args=(coupon.poolroom.uuid,)))
                reply.append((u"俱乐部详情", coupon.poolroom.name, picurl, weblink))
        return reply
    
    def buildAbsoluteURI(self, relativeURI):
        try:
            if 'pkbilliard.com' in self.request.META['HTTP_HOST'] or 'pkbilliard.com' in self.request.META['HTTP_HOST']:
                return set_query_parameter(self.request.build_absolute_uri(relativeURI), 'from', self.getFromSoureStr())
        except KeyError:
            pass
        return set_query_parameter("http://%s%s" %(SITE_DOMAIN, relativeURI), 'from', self.getFromSoureStr())
    
    def getSpecialEventItem(self, receivedtime):
        reply = []
        events = self.hasSpecialEvent(receivedtime)
        if events is not None:
            for event in events:
                reply.append((event.title, event.description, event.picAD if event.picAD != '' else LOGO_IMG_URL, 
                    self.buildAbsoluteURI(reverse('event_year_month_name', args=(event.year, "%02d" % (event.month,), event.titleabbrev,)))))
        return reply
        
    def getWelcomeMsg(self):
        return [(u'欢迎您关注我为台球狂官方微信', 
                 u'获取更多身边俱乐部信息，请访问：http://%s，与我们更多互动，发送您的位置信息给我们，为您推荐身边的台球俱乐部。发送 ？，帮助，获取帮助手册。' %(SITE_DOMAIN),
                LOGO_IMG_URL, 'http://mp.weixin.qq.com/s?__biz=MzA5MzY0MTYxMw==&mid=202621318&idx=1&sn=a0987cfafc05158fa0c35a0ba46b5701#rd')]
        
    def getHelpMesg(self):
        return [(HELP_TITLE, u'"活动一：预约送饮料； 活动二：消费返红包； 活动三：天天领红包；', 'http://bcs.duapp.com/billiardsalbum/2015/02/sales.jpg', 'http://mp.weixin.qq.com/s?__biz=MzA5MzY0MTYxMw==&mid=202723018&idx=1&sn=4c249995b4a57ab00453f959b60f7b8f#rd')]
    
    def help(self):
        def helpmessge(message):
            reply = self.getSpecialEventItem(message.time)
            reply += self.getHelpMesg()
            return reply
        return helpmessge
    
    def subscribe(self):
        def subscribe_handler(message):
            reply = self.getSpecialEventItem(message.time)
            reply += self.getWelcomeMsg()
            try:
                eventkey = message.EventKey
            except AttributeError:
                eventkey = None
            try:
                ticket = message.Ticket
            except AttributeError:
                ticket = None
            recordUserActivity(message, 'event', message.type, {'event': message.type, 'eventkey': eventkey, 'ticket': ticket}, None, self.target)
            return reply
        return subscribe_handler
    
    def scan(self):
        def scan_handler(message):
            reply = self.getSpecialEventItem(message.time)
            try:
                eventkey = message.EventKey
            except AttributeError:
                eventkey = None
            try:
                ticket = message.Ticket
            except AttributeError:
                ticket = None
            recordUserActivity(message, 'event', message.type, {'event': message.type, 'eventkey': eventkey, 'ticket': ticket}, None, self.target)
            return reply
        return scan_handler
    
    def unsubscribe(self):
        def unsubscribe_handler(message):
            recordUserActivity(message, 'event', message.type, {'event': message.type}, None, self.target)
            return DummyReply()
        return unsubscribe_handler
    
    def userlocation(self):
        def userlocation_hanlder(message):
            try:
                timeout = 60 * 60 * 24
                cache.set(KEY_PREFIX %('latlng', message.source), '%s,%s' %(str(message.latitude), str(message.longitude)), timeout)
                cache.set(KEY_PREFIX %('precision', message.source), str(message.precision), timeout)
                cache.set(KEY_PREFIX %('time', message.source), str(message.time), timeout)
                return DummyReply()
            except AttributeError:
                return None
        return userlocation_hanlder
    
    def getNearbyPoolroomsReply(self, message, lat, lng, size):
        baidu_loc = gcj2bd(float(lat),float(lng))
        baidu_loc_lat = unicode(baidu_loc[0])
        baidu_loc_lng = unicode(baidu_loc[1])
        nearbyPoolrooms = getNearbyPoolrooms(baidu_loc_lat, baidu_loc_lng, 3)[:size]
        return (nearbyPoolrooms, baidu_loc_lat, baidu_loc_lng)
    
    def location(self):
        def location_handler(message):
            try:
                lat = message.location[0]
                lng = message.location[1]
                nearbyPoolrooms, baidu_loc_lat, baidu_loc_lng = self.getNearbyPoolroomsReply(message, lat, lng, 1)
                reply = self.getSpecialEventItem(message.time)
                if len(nearbyPoolrooms) > 0:
                    poolroom = nearbyPoolrooms[0]
                    reply += self.getNewsPoolroomsReply(nearbyPoolrooms)
                    nativetime = datetime.utcfromtimestamp(float(message.time))
                    localtz = pytz.timezone(settings.TIME_ZONE)
                    localtime = localtz.localize(nativetime)
                    coupons = poolroom.getCoupons(localtime)
                    reply += self.getCouponsReply(coupons)
                    
                    recordUserActivity(message, 'location', poolroom.name, {'lat': lat, 'lng': lng, 'scale': message.scale, 'label': ['Label']}, 
                                       {'id': poolroom.id, 'name': poolroom.name, 'distance': poolroom.location_distance.km}, self.target)
                else:
                    reply.append((u"在您附近3公里以内，没有推荐的台球俱乐部，去其他地方试试吧", '', LOGO_IMG_URL, ''))
                    recordUserActivity(message, 'location', '', {'lat': lat, 'lng': lng, 'scale': message.scale, 'label': ['Label']}, 
                                       None, self.target)
                    
                challengeReply = self.getChallengeReply(message, baidu_loc_lat, baidu_loc_lng)
                nearbyChallenges = getNearbyChallenges(lat, lng, 5, datetime.utcfromtimestamp(float(message.time)))[:MAX_NEWSITEM - len(reply) - len(challengeReply)]
                reply.append(challengeReply[0])
                reply += self.getNearbyChallengeReply(nearbyChallenges)
                reply.append(challengeReply[1])
                return reply
            except AttributeError:
                return None
        return location_handler
    
    def pic(self):
        def reply(message):
            return self.picReply(message)
        return reply
    
    def picReply(self, message):
        pics = set_pic()
        picid = randint(0,len(pics)-1)
        return ImageReply(message, media_id=pics[picid])
    
    def getActs(self, time):
        nativetime = datetime.utcfromtimestamp(time)
        localtz = pytz.timezone(settings.TIME_ZONE)
        starttime = localtz.localize(nativetime)
        return getMatchByRequest(self.request, starttime, deltadays=7)[0].filter(type=2)
    
    def getPKCoupon(self, reply, message, source = 'text'):
        content = None
        if isinstance(message, TextMessage): 
            content = message.content
        elif isinstance(message, EventMessage):
            content = message.key
        
        nativetime = datetime.utcfromtimestamp(float(message.time))
        localtz = pytz.timezone(settings.TIME_ZONE)
        localtime = localtz.localize(nativetime)
        
        latlngstr = cache.get(KEY_PREFIX %('latlng', message.source))
        if latlngstr == None:
            coupons = Coupon.objects.filter(getCouponCriteria(localtime)).order_by('?')[:3]
        else:
            latlngs = latlngstr.split(',')
            baidu_loc = gcj2bd(float(latlngs[0]),float(latlngs[1]))
            baidu_loc_lat = unicode(baidu_loc[0])
            baidu_loc_lng = unicode(baidu_loc[1])
            poolrooms = Coupon.objects.filter(getCouponCriteria(localtime)).values_list('poolroom', flat=True).distinct()
            nearby = getNearbyPoolrooms(baidu_loc_lat, baidu_loc_lng, 10, None).filter(id__in=poolrooms)[:3]
            np_ids = []
            for np in nearby:
                np_ids.append(np.id)
            coupons = Coupon.objects.filter(getCouponCriteria(localtime)).filter(poolroom__in=np_ids)
            coupons_sorted = list()
            for pid in np_ids:
                coupons_sorted.append(coupons.get(poolroom=pid))
            coupons = coupons_sorted
        if len(coupons) > 0:
            recordUserActivity(message, source, 'coupon', {'content': content}, 
                           {'count': len(coupons), 'coupon': True}, self.target)
            reply += self.getCouponsReply(coupons, True)
        else:
            recordUserActivity(message, source, 'nocoupon', {'content': content}, None, self.target)
            data = u'附近的俱乐部暂时没有"优惠"或"团购"。'
            reply.append((data, data, SITE_LOGO_URL, ''))
        return reply
    
    def getPKActivity(self, reply, message, source = 'text'):
        content = None
        if isinstance(message, TextMessage): 
            content = message.content
        elif isinstance(message, EventMessage):
            content = message.key
        acts = self.getActs(float(message.time))
        count = acts.count()
        if count > 0:
            acts = acts[:MAX_NEWSITEM - len(reply)]
            reply += self.getActsReply(acts)
            recordUserActivity(message, source, 'activity', {'content': content}, 
                           {'count': len(acts), 'activity': True}, self.target)
        else:
            data = u'最近7天内没有被收录的爱好者活动'
            recordUserActivity(message, source, 'noactivity', {'content': content}, 
                           None, self.target)
            reply.append((data, data, SITE_LOGO_URL, ''))
        return reply
    
    def getPKPoolroomNearby(self, reply, message, source = 'text'):
        latlngstr = cache.get(KEY_PREFIX %('latlng', message.source))
        reply = self.getSpecialEventItem(message.time)
        if latlngstr == None:
            reply.append((u"点此查看周边球房", u'获取您的位置失败，点此查看周边球房', LOGO_IMG_URL, self.buildAbsoluteURI(reverse('poolroom_nearby', args=()))))
            return reply
        
        latlngs = latlngstr.split(',')
        nearbyPoolrooms, baidu_loc_lat, baidu_loc_lng = self.getNearbyPoolroomsReply(message, latlngs[0], latlngs[1], MAX_NEWSITEM - len(reply))
        if len(nearbyPoolrooms) > 0:
            newsAvaileSize = MAX_NEWSITEM - len(reply) - len(nearbyPoolrooms)
            ids, names, distances = ([], [], [])
            for poolroom in nearbyPoolrooms:
                ids.append(str(poolroom.id))
                names.append(poolroom.name)
                distances.append(str(poolroom.location_distance.km))
                reply += self.getNewsPoolroomsReply([poolroom])
                if newsAvaileSize > 0:
                    nativetime = datetime.utcfromtimestamp(float(message.time))
                    localtz = pytz.timezone(settings.TIME_ZONE)
                    localtime = localtz.localize(nativetime)
                    coupons = poolroom.getCoupons(localtime)
                    couponsreplies = self.getCouponsReply(coupons)[:newsAvaileSize]
                    reply += couponsreplies
                    newsAvaileSize -= len(couponsreplies)
                    
            recordUserActivity(message, 'location', 'click', {'lat': latlngs[0], 'lng': latlngs[1], 'user': message.source}, 
                {'id': ','.join(ids), 'name': ','.join(names), 'distance': ','.join(distances)}, self.target)
        else:
            reply.append((u"在您附近3公里以内，没有推荐的台球俱乐部，去其他地方试试吧", '', LOGO_IMG_URL, ''))
            recordUserActivity(message, 'location', 'click', {'lat': latlngs[0], 'lng': latlngs[1], 'user': message.source}, 
                               None, self.target)
        return reply
    
    def getPKAssistantRecommend(self, reply, message, source = 'event'):
        def assistantReply(offer):
            try:
                poolroomname = Poolroom.objects.get(id=offer.poolroom).name
            except:
                poolroomname = ''
            return (offer.assistant.nickname, poolroomname, "%s%s" %(settings.MEDIA_URL[:-1], offer.assistant.coverimage), 
                    self.buildAbsoluteURI(reverse('assistant_detail', args=(str(offer.assistant.uuid), ))))
        latlngstr = cache.get(KEY_PREFIX %('latlng', message.source))
        reply = self.getSpecialEventItem(message.time)
        if latlngstr == None:
            offer = getAssistantOffers().order_by('?')[0]
            ar = assistantReply(AssistantOffer.objects.get(id=offer['id']))
            reply.append(ar)
            return reply
        
        latlngs = latlngstr.split(',')
        baidu_loc = gcj2bd(float(latlngs[0]),float(latlngs[1]))
        baidu_loc_lat = unicode(baidu_loc[0])
        baidu_loc_lng = unicode(baidu_loc[1])
        poolrooms = AssistantOffer.objects.filter(ASSISTANT_OFFER_FILTER).values_list('poolroom', flat=True).distinct()
        nearby = getNearbyPoolrooms(baidu_loc_lat, baidu_loc_lng, None, None).filter(id__in=poolrooms)[0]
        ar = assistantReply(AssistantOffer.objects.filter(ASSISTANT_OFFER_FILTER).filter(poolroom=nearby.id).order_by('?')[0])
        reply.append(ar)
        return reply
        
    def getPKMatch(self, reply, message, source = 'text'):
        nativetime = datetime.utcfromtimestamp(float(message.time))
        localtz = pytz.timezone(settings.TIME_ZONE)
        starttime = localtz.localize(nativetime)
        matches, starttime, endtime = getMatchByRequest(self.request, starttime, deltadays=7)
        matches = matches.filter(type=1)
        count = matches.count()
        if count > 0:
            matches = matches[:MAX_NEWSITEM - len(reply)]
            reply += self.getMatchesReply(matches)
            content = None
            if isinstance(message, TextMessage): 
                content = message.content
            elif isinstance(message, EventMessage):
                content = message.key
            recordUserActivity(message, source, 'match' if source == 'event' else message.type, {'content': content}, 
                           {'count': len(matches), 'match': True}, self.target)       
        else:
            data = '最近7天内没有被收录的比赛'
            content = source
            recordUserActivity(message, source, 'nomatch', {'content': content}, 
                           None, self.target)
            reply.append((data, data, SITE_LOGO_URL, ''))
        return reply
    
    def applyMember(self, reply, message, targetgroup):
        group = Group.objects.get(Q(id=targetgroup))
        try:
            member = Membership.objects.get(Q(wechatid=message.source) & Q(targetid=targetgroup))
            reply = [(u"你已经是'%s'会员啦！" %(group.name), u'我的会员号: %s' %(member.memberid), '', self.buildAbsoluteURI(reverse('membership', args=(message.source, targetgroup,))))]
        except Membership.DoesNotExist:
            reply = [(u"欢迎申请'%s'会员卡" %(group.name), u"点击我只需一步就成为'%s'会员" %(group.name), '', self.buildAbsoluteURI(reverse('membership_apply', args=(message.source, targetgroup,))))]
        return reply
    
    def queryMember(self, reply, message, targetgroup):
        group = Group.objects.get(Q(id=targetgroup))
        try:
            member = Membership.objects.get(Q(wechatid=message.source) & Q(targetid=targetgroup))
            reply = [(u"%s, 欢迎你成为'%s'会员" %(member.name, group.name), u'我的会员号: %s' %(member.memberid), '', self.buildAbsoluteURI(reverse('membership', args=(message.source, targetgroup,))))]
        except Membership.DoesNotExist:
            reply = [(u"你还不是'%s'会员" %(group.name), u"点击我只需一步就成为'%s'会员" %(group.name), '', self.buildAbsoluteURI(reverse('membership_apply', args=(message.source, targetgroup,))))]
        return reply
    
    def getAssistantInfo(self, message):
        try:
            user = User.objects.get(username=message.source)
            return AssistantUser.objects.get(user=user)
        except User.DoesNotExist:
            return None
        except AssistantUser.DoesNotExist:
            return None
    def text(self):    
        def text_handler(message):
            qqface = "/::\\)|/::~|/::B|/::\\||/:8-\\)|/::<|/::$|/::X|/::Z|/::'\\(|/::-\\||/::@|/::P|/::D|/::O|/::\\(|/::\\+|/:--b|/::Q|/::T|/:,@P|/:,@-D|/::d|/:,@o|/::g|/:\\|-\\)|/::!|/::L|/::>|/::,@|/:,@f|/::-S|/:\\?|/:,@x|/:,@@|/::8|/:,@!|/:!!!|/:xx|/:bye|/:wipe|/:dig|/:handclap|/:&-\\(|/:B-\\)|/:<@|/:@>|/::-O|/:>-\\||/:P-\\(|/::'\\||/:X-\\)|/::\\*|/:@x|/:8\\*|/:pd|/:<W>|/:beer|/:basketb|/:oo|/:coffee|/:eat|/:pig|/:rose|/:fade|/:showlove|/:heart|/:break|/:cake|/:li|/:bome|/:kn|/:footb|/:ladybug|/:shit|/:moon|/:sun|/:gift|/:hug|/:strong|/:weak|/:share|/:v|/:@\\)|/:jj|/:@@|/:bad|/:lvu|/:no|/:ok|/:love|/:<L>|/:jump|/:shake|/:<O>|/:circle|/:kotow|/:turn|/:skip|/:oY|/:#-0|/:hiphot|/:kiss|/:<&|/:&>"
            match = re.search(message.content, qqface)
            content = set_content()
            if message.content in content.keys():
                reply = content[message.content]    
            elif match:
                reply = message.content
            else:
                reply = self.getSpecialEventItem(message.time)
                if message.content == u"图片" or message.content == u"墙纸":
                    reply = self.picReply(message)
                elif message.content == u"花式" or message.content == u"花式台球":
                    videos = set_video()
                    videoid = randint(0,len(videos)-1)
                    reply.append((videos[videoid]['title'], videos[videoid]['description'], videos[videoid]['plink'], videos[videoid]['vlink']))
                elif message.content == u"中式八球" or message.content == u"中式" or message.content == u"zsbq":
                    videos = set_zsbq_video()
                    videoid = randint(0,len(videos)-1)
                    reply.append((videos[videoid]['title'], videos[videoid]['description'], videos[videoid]['plink'], videos[videoid]['vlink'])) 
                elif message.content == u"团购" or message.content == u"找便宜" or message.content == u"优惠":
                    reply = self.keysHandlers["PK_COUPON"](reply, message)
                elif message.content == u"云川" or message.content == u"yunchuan" or message.content == u"yc":
                    nativetime = datetime.utcfromtimestamp(float(message.time))
                    localtz = pytz.timezone(settings.TIME_ZONE)
                    localtime = localtz.localize(nativetime)
                    coupons = Coupon.objects.filter(getCouponCriteria(localtime)).filter(poolroom__in=Poolroom.objects.filter(name__startswith=u'北京云川')).order_by('?')[:1]
                    if len(coupons) > 0:
                        recordUserActivity(message, 'text', 'yunchuan', {'content': message.content}, 
                                       {'count': len(coupons), 'yunchuan_coupon': True}, self.target)
                        reply += self.getCouponsReply(coupons, True)
                    else:
                        data = u'云川俱乐部暂没有优惠。请输入"优惠"或"团购“查找其他俱乐部的优惠。'
                        recordUserActivity(message, 'text', 'noyunchuan', {'content': message.content}, 
                                       None, self.target)
                        reply.append((data, data, SITE_LOGO_URL, ''))
                elif message.content == u"活动":
                    reply = self.keysHandlers["PK_ACTIVITY"](reply, message)
                elif message.content == u"比赛":
                    reply = self.keysHandlers["PK_MATCH"](reply, message)
                elif message.content == u'会员卡':
                    reply = self.applyMember(reply, message, 4)
                elif message.content == u'查看会员卡':
                    reply = self.queryMember(reply, message, 4)
                elif message.content in HELP_KEYWORDS:
                    reply += self.getHelpMesg()
                elif message.content == u'订单' and self.getAssistantInfo(message) != None:
                    au = self.getAssistantInfo(message)
                    reply = []
                    reply.append((u'%s的订单' %(au.assistant.nickname), u'订单详情', "%s%s" %(settings.MEDIA_URL[:-1], au.assistant.coverimage), 
                                  self.buildAbsoluteURI(reverse('assistant_orders', args=(str(au.assistant.uuid), )))))
                else:
                    reply += self.getHelpMesg()
                    recordUserActivity(message, 'text', message.content, {'content': message.content}, 
                                           None, self.target)
            return reply
        return text_handler
    
    def echo(self, request):
        try:
            if not self.check_signature(
                    request.GET.get('timestamp'),
                    request.GET.get('nonce'),
                    request.GET.get('signature')
                    ):
                raise PermissionDenied
            return HttpResponse(request.GET.get('echostr'))
        except:
            raise PermissionDenied

    def handle(self, request):
        if not settings.TESTING and not self.check_signature(
            request.GET.get('timestamp'),
            request.GET.get('nonce'),
            request.GET.get('signature')
        ):
            raise PermissionDenied

        body = smart_str(request.body)
        message = parse_user_msg(body)
        self.logger.info("Receive message %s" % message)
        reply = self.get_reply(message)
        if not reply:
            errMsg = "No proper handler responded message %s" %(message.type)
            self.logger.warning(errMsg)
            return HttpResponse(errMsg)
        return HttpResponse(create_reply(reply, message=message), content_type="application/xml")

@csrf_exempt
def weixin(request):
    robot = PKWechat("pkbilliard", request)
    if request.method=='GET':
        return robot.echo(request)
    elif request.method=='POST':
        return robot.handle(request)

class PKWechatService(PKWechat):
    def getFromSoureStr(self):
        return 'wechat-service'
    
@csrf_exempt
def wechat(request):
    robot = PKWechatService("Iwk0IlxqidGPYbAeEAeQ4K1f1hym76", request, 0)
    if request.method=='GET':
        return robot.echo(request)
    elif request.method=='POST':
        return robot.handle(request)
    
def updateUserInfo(jsonstr):
    userObjs = simplejson.loads(jsonstr)
    for user in userObjs:
        user['fields']['firstjoin'] = True if WechatActivity.objects.filter(
            Q(receivedtime__lt=user['fields']['receivedtime']) & Q(keyword='unsubscribe') & Q(userid=user['fields']['userid'])).count() == 0 else False
        unsubEvents = WechatActivity.objects.filter(
            Q(receivedtime__gt=user['fields']['receivedtime']) & Q(keyword='unsubscribe') & Q(userid=user['fields']['userid']))
        if unsubEvents.count() == 0:
            user['fields']['unsubscribed'] = False
        else:
            user['fields']['unsubscribed'] = True
            user['fields']['unsubscribedDate'] = unsubEvents.order_by('-receivedtime')[:1][0].receivedtime.strftime('%b %d %Y %H:%M:%S %Z')
    return simplejson.dumps(userObjs)

@ensure_csrf_cookie
def activity_report_newuser(request):
    if not request.user.is_authenticated() or not request.user.is_staff:
        raise PermissionDenied
    if request.method == 'POST':
        startdate = datetime.fromtimestamp(float(request.POST['startdate'])/1000, pytz.timezone(TIME_ZONE))
        enddate = datetime.fromtimestamp(float(request.POST['enddate'])/1000, pytz.timezone(TIME_ZONE))
        enddate = relativedelta(days=1) + enddate
        subscribeEvents = WechatActivity.objects.filter(Q(receivedtime__gte=startdate) & Q(receivedtime__lt=enddate) & Q(eventtype='event')
                & Q(keyword='subscribe')).distinct().order_by('receivedtime')
        
        paginator = Paginator(subscribeEvents, 10)
        page = 1
        try:
            page = request.GET.get('page')
        except Exception:
            pass
        try:
            subscribers = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            subscribers = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            subscribers = paginator.page(paginator.num_pages)
        json_serializer = DisplayNameJsonSerializer()
        stream = StringIO()
        json_serializer.serialize(subscribers, fields=('userid', 'keyword', 'receivedtime', 'target'), stream=stream,
            ensure_ascii=False, use_natural_keys=True)
        jsonstr = stream.getvalue()
        jsonstr = updateUserInfo(jsonstr)
        jsonstr = updatePageInfo(jsonstr, subscribers)
        return HttpResponse(jsonstr, mimetype="application/json")
    return render_to_response(TEMPLATE_ROOT + 'wechat/newuser.html', 
                              {'REPORT_TITLE' : u'新用户统计'},
                              context_instance=RequestContext(request))
    
def updatePageInfo(jsonstr, paging):
    objs = simplejson.loads(jsonstr)
    class Activity(object):
        pass
    activity = Activity()
    setattr(activity, 'page', paging.number)
    setattr(activity, 'count', paging.paginator.num_pages)
    setattr(activity, 'data', objs)
    return simplejson.dumps(activity.__dict__)

@ensure_csrf_cookie
def activity_report_message(request):
    if not request.user.is_authenticated() or not request.user.is_staff:
        raise PermissionDenied
    if request.method == 'POST':
        startdate = datetime.fromtimestamp(float(request.POST['startdate'])/1000, pytz.timezone(TIME_ZONE))
        enddate = datetime.fromtimestamp(float(request.POST['enddate'])/1000, pytz.timezone(TIME_ZONE))
        enddate = relativedelta(days=1) + enddate
        messageEvents = WechatActivity.objects.filter(Q(receivedtime__gte=startdate) & Q(receivedtime__lt=enddate) & ~Q(eventtype='event')).order_by('receivedtime')
        paginator = Paginator(messageEvents, 10)
        page = 1
        try:
            page = request.GET.get('page')
        except Exception:
            pass
        try:
            messages = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            messages = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            messages = paginator.page(paginator.num_pages)
        json_serializer = DisplayNameJsonSerializer()
        stream = StringIO()
        json_serializer.serialize(messages, fields=('userid', 'eventtype', 'keyword', 'receivedtime', 'message', 'target'), stream=stream,
            ensure_ascii=False, use_natural_keys=True)
        jsonstr = stream.getvalue()
        jsonstr = updatePageInfo(jsonstr, messages)
        return HttpResponse(jsonstr, mimetype="application/json")
    return render_to_response(TEMPLATE_ROOT + 'wechat/message.html', 
                              {'REPORT_TITLE': u'用户消息统计'},
                              context_instance=RequestContext(request))

def activity_report(request):
    if not request.user.is_authenticated() or not request.user.is_staff:
        raise PermissionDenied
    return render_to_response(TEMPLATE_ROOT + 'wechat/report.html', 
                              {'REPORT_TITLE': u'微信用户消息统计'},
                              context_instance=RequestContext(request))
