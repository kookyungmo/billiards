# coding=utf-8
from StringIO import StringIO
from datetime import datetime, timedelta
import re
import logging
from urllib import urlencode
from urlparse import urlsplit, parse_qs, urlunsplit

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
from werobot.parser import parse_user_msg
from werobot.reply import create_reply, WeChatReply
from werobot.robot import BaseRoBot

from billiards import settings
from billiards.bcms import mail
from billiards.location_convertor import gcj2bd
from billiards.models import Coupon, getCouponCriteria, Poolroom, PoolroomImage, \
    WechatActivity, DisplayNameJsonSerializer, Event
from billiards.settings import TEMPLATE_ROOT, TIME_ZONE, SITE_LOGO_URL
from billiards.views.challenge import getNearbyChallenges
from billiards.views.match import getMatchByRequest
from billiards.views.poolroom import getNearbyPoolrooms
from dateutil.relativedelta import relativedelta
from Crypto.Random.random import randint
from werobot.utils import to_text

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

def recordUserActivity(userid, event, keyword, message, receivedtime, reply, target = 1):
    nativetime = datetime.utcfromtimestamp(float(receivedtime))
    localtz = pytz.timezone(settings.TIME_ZONE)
    localtime = nativetime.replace(tzinfo=timezone.utc).astimezone(tz=localtz)
    newactivity = WechatActivity.objects.create_activity(userid, event, keyword, simplejson.dumps(message).decode('unicode-escape'), localtime, None if reply == None else simplejson.dumps(reply).decode('unicode-escape'), target)
    if event in settings.WECHAT_ACTIVITY_TRACE:
        newactivity.save()
        
    if not settings.TESTING and (event in settings.WECHAT_ACTIVITY_NOTIFICATION or keyword in settings.WECHAT_ACTIVITY_NOTIFICATION_KEYWORDS):
        mail(settings.NOTIFICATION_EMAIL, u'New wechat activity -- %s' %(localtime), 
             u'[%s][%s] The "%s" message %s from "%s" was received at %s.' %(newactivity.get_target_display(), event, keyword, simplejson.dumps(message).decode('unicode-escape'), userid, localtime))

def set_query_parameter(url, param_name, param_value):
    """Given a URL, set or replace a query parameter and return the
    modified URL.

    >>> set_query_parameter('http://example.com?foo=bar&biz=baz', 'foo', 'stuff')
    'http://example.com?foo=stuff&biz=baz'

    """
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)

    query_params[param_name] = [param_value]
    new_query_string = urlencode(query_params, doseq=True)

    return urlunsplit((scheme, netloc, path, new_query_string, fragment))

def buildPoolroomImageURL(poolroom):
    if poolroom.images.count() > 0:
        coverimage = poolroom.images.filter(iscover=1)
        if len(coverimage) > 0:
            return "%s%s" %(settings.MEDIA_ROOT, PoolroomImage.getThumbnailPath(coverimage[0].imagepath.name, 300))
        return "%s%s" %(settings.MEDIA_ROOT, PoolroomImage.getThumbnailPath(poolroom.images[:1][0].imagepath.name, 300))
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
    
class PKWechat(BaseRoBot):
    def __init__(self, token, request, target = 1):
        super(PKWechat, self).__init__(token, enable_session=False)
        self.request = request
        self.target = target
        self.addHandlers()
        
    def addHandlers(self):
        self.add_handler(self.subscribe(), 'subscribe')
        self.add_handler(self.unsubscribe(), 'unsubscribe')
        self.add_handler(self.location(), 'location')
        self.add_handler(self.text(), 'text')
        self.add_handler(self.pic(), 'image')
        self.add_handler(self.help(), 'all')
        
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
            originContent = self.buildAbsoluteURI(reverse('poolroom_detail', args=(pkid,)))
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
            reply.append(((u"%s发起距离你%s公里的抢台费" %(challenge.issuer_nickname, "{0:.2f}".format(challenge.distance))), u"抢台费的地点: %s" %(loc), LOGO_IMG_URL, challlengelink))
        return reply
    
    def getCouponsReply(self, coupons, withPoolroom = False):
        reply = []
        for coupon in coupons:
            picurl = buildPoolroomImageURL(coupon.poolroom)
            couponurl = self.buildAbsoluteURI(reverse('coupontracker', args=(coupon.id,)))
            reply.append((coupon.title, coupon.description, picurl, couponurl))
            if withPoolroom:
                picurl = buildPoolroomImageURL(coupon.poolroom)
                weblink = self.buildAbsoluteURI(reverse('poolroom_detail', args=(coupon.poolroom.pk,)))
                reply.append((u"俱乐部详情", coupon.poolroom.name, picurl, weblink))
        return reply
    
    def buildAbsoluteURI(self, relativeURI):
        try:
            if 'pktaiqiu.com' in self.request.META['HTTP_HOST']:
                return set_query_parameter(self.request.build_absolute_uri(relativeURI), 'from', self.getFromSoureStr())
        except KeyError:
            pass
        return set_query_parameter("http://www.pktaiqiu.com%s" %(relativeURI), 'from', self.getFromSoureStr())
    
    def getSpecialEventItem(self, receivedtime):
        reply = []
        events = self.hasSpecialEvent(receivedtime)
        if events is not None:
            for event in events:
                reply.append((event.title, event.description, event.picAD if event.picAD != '' else LOGO_IMG_URL, 
                    self.buildAbsoluteURI(reverse('event_year_month_name', args=(event.year, "%02d" % (event.month,), event.titleabbrev,)))))
        return reply
        
    def getWelcomeMsg(self):
        return [(u'欢迎您关注我为台球狂官方微信', u'获取更多身边俱乐部信息，请访问：http://www.pktaiqiu.com，与我们更多互动，发送您的位置信息给我们，为您推荐身边的台球俱乐部。发送 ？，帮助，获取帮助手册。',
                LOGO_IMG_URL, 'http://mp.weixin.qq.com/s?__biz=MzA3MzE5MTEyOA==&mid=200093832&idx=1&sn=16041cf184f816bb2ae37db15847e621#rd')]
        
    def getHelpMesg(self):
        return [(u'"我为台球狂"微信帮助手册', u'"我为台球狂"微信帮助手册', LOGO_IMG_URL, 'http://mp.weixin.qq.com/s?__biz=MzA3MzE5MTEyOA==&mid=200093857&idx=1&sn=05527c469c9ba83c320262f3b7744125#rd')]
    
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
                eventkey = message.key
            except AttributeError:
                eventkey = None
            recordUserActivity(message.source, 'event', message.type, {'event': message.type, 'eventkey': eventkey}, message.time, None, self.target)
            return reply
        return subscribe_handler
    
    def unsubscribe(self):
        def unsubscribe_handler(message):
            recordUserActivity(message.source, 'event', message.type, {'event': message.type}, message.time, None, self.target)
        return unsubscribe_handler
    
    def location(self):
        def location_handler(message):
            lat = message.location[0]
            lng = message.location[1]
            baidu_loc = gcj2bd(float(lat),float(lng))
            baidu_loc_lat = unicode(baidu_loc[0])
            baidu_loc_lng = unicode(baidu_loc[1])
            nearbyPoolrooms = getNearbyPoolrooms(baidu_loc_lat, baidu_loc_lng, 3)[:1]
            reply = self.getSpecialEventItem(message.time)
            if len(nearbyPoolrooms) > 0:
                poolroom = nearbyPoolrooms[0]
                reply += self.getNewsPoolroomsReply(nearbyPoolrooms)
                nativetime = datetime.utcfromtimestamp(float(message.time))
                localtz = pytz.timezone(settings.TIME_ZONE)
                localtime = localtz.localize(nativetime)
                coupons = poolroom.getCoupons(localtime)
                reply += self.getCouponsReply(coupons)
                
                recordUserActivity(message.source, 'location', poolroom.name, {'lat': lat, 'lng': lng, 'scale': message.scale, 'label': ['Label']}, message.time, 
                                   {'id': poolroom.id, 'name': poolroom.name, 'distance': poolroom.distance}, self.target)
            else:
                reply.append((u"在您附近3公里以内，没有推荐的台球俱乐部，去其他地方试试吧", '', LOGO_IMG_URL, ''))
                recordUserActivity(message.source, 'location', '', {'lat': lat, 'lng': lng, 'scale': message.scale, 'label': ['Label']}, message.time, 
                                   None, self.target)
                
            challengeReply = self.getChallengeReply(message, baidu_loc_lat, baidu_loc_lng)
            nearbyChallenges = getNearbyChallenges(lat, lng, 5, datetime.utcfromtimestamp(float(message.time)))[:MAX_NEWSITEM - len(reply) - len(challengeReply)]
            reply.append(challengeReply[0])
            reply += self.getNearbyChallengeReply(nearbyChallenges)
            reply.append(challengeReply[1])
            return reply
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
                    nativetime = datetime.utcfromtimestamp(float(message.time))
                    localtz = pytz.timezone(settings.TIME_ZONE)
                    localtime = localtz.localize(nativetime)
                    coupons = Coupon.objects.filter(getCouponCriteria(localtime)).order_by('?')[:3]
                    if len(coupons) > 0:
                        recordUserActivity(message.source, 'text', 'coupon', {'content': message.content}, message.time, 
                                       {'count': len(coupons), 'coupon': True}, self.target)
                        reply += self.getCouponsReply(coupons, True)
                    else:
                        recordUserActivity(message.source, 'text', 'nocoupon', {'content': message.content}, message.time, None, self.target)
                        data = u'暂时没有俱乐部有"优惠"或"团购"。'
                        reply.append((data, data, SITE_LOGO_URL, ''))
                elif message.content == u"云川" or message.content == u"yunchuan" or message.content == u"yc":
                    nativetime = datetime.utcfromtimestamp(float(message.time))
                    localtz = pytz.timezone(settings.TIME_ZONE)
                    localtime = localtz.localize(nativetime)
                    coupons = Coupon.objects.filter(getCouponCriteria(localtime)).filter(poolroom__in=Poolroom.objects.filter(name__startswith=u'北京云川')).order_by('?')[:1]
                    if len(coupons) > 0:
                        recordUserActivity(message.source, 'text', 'yunchuan', {'content': message.content}, message.time, 
                                       {'count': len(coupons), 'yunchuan_coupon': True}, self.target)
                        reply += self.getCouponsReply(coupons, True)
                    else:
                        data = u'云川俱乐部暂没有优惠。请输入"优惠"或"团购“查找其他俱乐部的优惠。'
                        recordUserActivity(message.source, 'text', 'noyunchuan', {'content': message.content}, message.time, 
                                       None, self.target)
                        reply.append((data, data, SITE_LOGO_URL, ''))
                elif message.content == u"活动":
                    acts = self.getActs(float(message.time))
                    count = acts.count()
                    if count > 0:
                        acts = acts[:MAX_NEWSITEM - len(reply)]
                        reply += self.getActsReply(acts)
                        recordUserActivity(message.source, 'text', 'activity', {'content': message.content}, message.time, 
                                       {'count': len(acts), 'activity': True}, self.target)
                    else:
                        data = u'最近7天内没有被收录的爱好者活动'
                        recordUserActivity(message.source, 'text', 'noactivity', {'content': message.content}, message.time, 
                                       None, self.target)
                        reply.append((data, data, SITE_LOGO_URL, ''))
                elif message.content == u"比赛":
                    nativetime = datetime.utcfromtimestamp(float(message.time))
                    localtz = pytz.timezone(settings.TIME_ZONE)
                    starttime = localtz.localize(nativetime)
                    matches, starttime, endtime = getMatchByRequest(self.request, starttime, deltadays=7)
                    matches = matches.filter(type=1)
                    count = matches.count()
                    if count > 0:
                        matches = matches[:MAX_NEWSITEM - len(reply)]
                        reply += self.getMatchesReply(matches)
                        recordUserActivity(message.source, 'text', 'match', {'content': message.content}, message.time, 
                                       {'count': len(matches), 'match': True}, self.target)       
                    else:
                        data = '最近7天内没有被收录的比赛'
                        recordUserActivity(message.source, 'text', 'nomatch', {'content': message.content}, message.time, 
                                       None, self.target)
                        reply.append((data, data, SITE_LOGO_URL, ''))
                elif message.content in HELP_KEYWORDS:
                    reply += self.getHelpMesg()
                else:
                    reply += self.getHelpMesg()
                    recordUserActivity(message.source, 'text', message.content, {'content': message.content}, message.time, 
                                           None, self.target)
            return reply
        return text_handler
    
    def echo(self, request):
        if not self.check_signature(
                request.GET.get('timestamp'),
                request.GET.get('nonce'),
                request.GET.get('signature')
                ):
            raise PermissionDenied
        return HttpResponse(request.GET.get('echostr'))

    def handle(self, request):
        if not settings.TESTING and not self.check_signature(
            request.GET.get('timestamp'),
            request.GET.get('nonce'),
            request.GET.get('signature')
        ):
            raise PermissionDenied

        body = smart_str(request.body)
        message = parse_user_msg(body)
        logging.info("Receive message %s" % message)
        reply = self.get_reply(message)
        if not reply:
            self.logger.warning("No handler responded message %s"
                                % message)
            return ''
        return HttpResponse(create_reply(reply, message=message), content_type="application/xml")

@csrf_exempt
def weixin(request):
    robot = PKWechat("pktaiqiu", request)
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
