# coding=utf-8
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
import hashlib, time, re
from random import randint
from xml.etree import ElementTree as ET

from billiards.location_convertor import gcj2bd
from billiards.views.poolroom import getNearbyPoolrooms
from django.core.urlresolvers import reverse
from billiards.models import Coupon, getCouponCriteria, Poolroom, PoolroomImage,\
    WechatActivity, EventCode, DisplayNameJsonSerializer, Event
from billiards.views.match import getMatchByRequest
from billiards import settings
import pytz
from django.utils import simplejson, timezone
from django.core.exceptions import PermissionDenied
from django.shortcuts import render_to_response
from billiards.settings import TEMPLATE_ROOT, TIME_ZONE, SITE_LOGO_URL
from django.template.context import RequestContext
from django.db.models.query_utils import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from StringIO import StringIO
from dateutil.relativedelta import relativedelta
from billiards.bcms import mail
from datetime import datetime, timedelta
from urlparse import urlsplit, parse_qs, urlunsplit
from urllib import urlencode

def checkSignature(request, token="pktaiqiu"):
    signature=request.GET.get('signature','')
    timestamp=request.GET.get('timestamp','')
    nonce=request.GET.get('nonce','')
    echostr=request.GET.get('echostr','')
    tmplist=[token,timestamp,nonce]
    tmplist.sort()
    tmpstr="%s%s%s"%tuple(tmplist)
    tmpstr=hashlib.sha1(tmpstr).hexdigest()
    if tmpstr==signature:
        return echostr
    else:
        return None
      
def parse_msg(request):
    recvmsg = smart_str(request.body)
    root = ET.fromstring(recvmsg)
    msg = {}
    for child in root:
        msg[child.tag] = child.text
    return msg

def set_video(request):
    videos = [
              {"title":"毒液花式台球史诗级巨制！神一般的弗洛里安·科勒(Florian Kohler)", "plink":"http://billiardsalbum.bcs.duapp.com/2014/02/FlorianKohler1.jpg","description":"绝对不能错过的精彩！点击观看","vlink":"http://v.youku.com/v_show/id_XNTU3MjMyNjI0.html"},
              {"title":"花式台球帝-毒液和他的彪悍女友 未来最疯狂的特技球家庭！", "plink":"http://billiardsalbum.bcs.duapp.com/2014/02/FlorianKohler1.jpg","description":"精彩不容错过！点击观看","vlink":"http://v.youku.com/v_show/id_XNTIxMjQzMzM2.html"},
              {"title":"毒液 最新花式台球集锦", "plink":"http://billiardsalbum.bcs.duapp.com/2014/02/FlorianKohler1.jpg","description":"精彩！犀利！点击观看","vlink":"http://v.youku.com/v_show/id_XNDQyNzI5MjEy.html"},
              {"title":"牛人和美女台球桌上玩花式台球", "plink":"http://billiardsalbum.bcs.duapp.com/2014/02/FlorianKohler1.jpg", "description":"点击观看\r\n时长：02:58", "vlink":"http://v.qq.com/boke/page/w/0/y/w0125gr8cny.html"},
              {"title":"花式台球 最美的境界 Venom Trickshots", "plink":"http://billiardsalbum.bcs.duapp.com/2014/02/FlorianKohler1.jpg","description":"精彩！高清！点击观看","vlink":"http://v.youku.com/v_show/id_XMzExMjIxMDgw.html"}
              ]
    return videos
  
def set_zsbq_video(request):
    videos = [
              {"title":"2013年首届中式八球大师邀请赛决赛 加雷斯·波茨vs克里斯·梅林", "plink":"http://billiardsalbum.bcs.duapp.com/2014/02/potts.jpg","description":"加雷斯·波茨vs克里斯·梅林 点击观看\r\n时长：93:47","vlink":"http://v.youku.com/v_show/id_XNDk4Nzc2OTg4.html"},
              {"title":"加雷斯·波茨——清台集锦", "plink":"http://billiardsalbum.bcs.duapp.com/2014/02/potts.jpg","description":"点击观看\r\n时长：57:20","vlink":"http://v.youku.com/v_show/id_XNjA4Njg4OTQ0.html"},
              {"title":"李赫文VS亨德利01-“英伦汽车·乔氏杯”亨德利中式八球挑战赛", "plink":"http://billiardsalbum.bcs.duapp.com/2014/02/hendry.jpg","description":"点击观看\r\n时长：82:46","vlink":"http://v.youku.com/v_show/id_XMzgzOTg2MjIw.html"}
              ]
    return videos

def set_pic(request):
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
  
def set_content(request):
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
  
#handle text message
textReplyTpl = """<xml>
         <ToUserName><![CDATA[%s]]></ToUserName>
         <FromUserName><![CDATA[%s]]></FromUserName>
         <CreateTime>%s</CreateTime>
         <MsgType><![CDATA[text]]></MsgType>
         <Content><![CDATA[%s]]></Content>
         <FuncFlag>0</FuncFlag>
         </xml>"""
#handle picture message
picReplyTpl = """<xml>
         <ToUserName><![CDATA[%s]]></ToUserName>
         <FromUserName><![CDATA[%s]]></FromUserName>
         <CreateTime>%s</CreateTime>
         <MsgType><![CDATA[image]]></MsgType>
         <Image>
         <MediaId><![CDATA[%s]]></MediaId>
         </Image>
         </xml>"""

#handle pic & text message
newsReplyTpl = """<xml>
         <ToUserName><![CDATA[%s]]></ToUserName>
         <FromUserName><![CDATA[%s]]></FromUserName>
         <CreateTime>%s</CreateTime>
         <MsgType><![CDATA[news]]></MsgType>
         <ArticleCount>%s</ArticleCount>
         <Articles>
         %s
         </Articles>
         <FuncFlag>1</FuncFlag>
         </xml>""" 
         
newsItemTpl = """<item>
         <Title><![CDATA[%s]]></Title> 
         <Description><![CDATA[%s]]></Description>
         <PicUrl><![CDATA[%s]]></PicUrl>
         <Url><![CDATA[%s]]></Url>
         </item>"""
         
CLUB_NAMES = {'22': (u'北京慧聚台球俱乐部', u'慧聚台球', u'慧聚', u'慧聚台球俱乐部')}
HELP_KEYWORDS = (u"帮助", u"?", u"？", u'help')

LOGO_IMG_URL = SITE_LOGO_URL

MAX_NEWSITEM = 10

NEWS_HELP = newsItemTpl %(u'"我为台球狂"微信帮助手册', u'"我为台球狂"微信帮助手册', LOGO_IMG_URL, 'http://mp.weixin.qq.com/s?__biz=MzA3MzE5MTEyOA==&mid=200093832&idx=1&sn=16041cf184f816bb2ae37db15847e621#rd')

def getNotFoundResponse(msg, specialEvent, data, newsSize = 0, news = ''):
    if specialEvent == None:
        return newsReplyTpl % (
            msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 1 + newsSize,
            newsItemTpl %(data, data, LOGO_IMG_URL, '') + news)
    return  newsReplyTpl % (
            msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 1 + specialEvent[0] + newsSize,
            specialEvent[1] + newsItemTpl %(data, data, LOGO_IMG_URL, '') + news)

def hasSpecialEvent(receivedtime):
    nativetime = datetime.utcfromtimestamp(float(receivedtime))
    localtz = pytz.timezone(settings.TIME_ZONE)
    localtime = localtz.localize(nativetime)
    extendtime = localtime + timedelta(days=3)
    events = Event.objects.filter(((Q(startdate__gte=localtime) & Q(startdate__lte=extendtime)) | Q(startdate__lte=extendtime)) & Q(enddate__gt=localtime))
    if events.count() > 0:
        return events
    return None

def getSpecialEventItem(request, receivedtime):
    events = hasSpecialEvent(receivedtime)
    if events is not None:
        eventTexts = ''
        for event in events:
            eventTexts += newsItemTpl %(event.title, event.description, event.picAD if event.picAD != '' else LOGO_IMG_URL, 
                buildAbsoluteURI(request, reverse('event_year_month_name', args=(event.year, "%02d" % (event.month,), event.titleabbrev,))))
        return (events.count(), eventTexts)
    return None


def getActNewsText(request, msg, acts, count, specialEvent):
    def getActsText(acts):
        text = []
        for act in acts:
            picurl = buildPoolroomImageURL(act.poolroom)
            text.append(newsItemTpl %(act.title, u"活动开始时间: %s" %(getNativeTime(act.starttime)), picurl, buildAbsoluteURI(request, reverse('activity_detail', args=(act.pk,)))))
        return ''.join(text)
    acts = acts[:MAX_NEWSITEM - (0 if specialEvent is None else specialEvent[0])]
    return newsReplyTpl % (
         msg['FromUserName'], msg['ToUserName'], str(int(time.time())), len(acts) + (specialEvent[0] if specialEvent != None else 0),
         (specialEvent[1] if specialEvent != None else '') + getActsText(acts))

def getNewsPoolroomsText(request, poolrooms):
    newstext = ''
    for poolroom in poolrooms:
        address = poolroom.address
        tel = poolroom.tel
        size = str(poolroom.size)
        pkid = unicode(poolroom.pk)
        businesshours = poolroom.businesshours
        picurl = buildPoolroomImageURL(poolroom)
        originContent = buildAbsoluteURI(request, reverse('poolroom_detail', args=(pkid,)))
        description = u"地址：%s\r\n营业面积：%s平方米\r\n营业时间：%s\r\n电话：%s" %(address, size, businesshours, tel)
        newstext = '%s%s' %(newstext, newsItemTpl %(poolroom.name, description, picurl, originContent))
    return newstext

def getChallengeNews(request, msg, lat, lng):
    publishlink = set_query_parameter(buildAbsoluteURI(request, reverse('challenge_publish', args=(lat, lng, 3,))), 'uid', msg['FromUserName'])
    challlengelink = buildAbsoluteURI(request, reverse('challenge_with_distance', args=(lat, lng,)))
    return u'%s%s' %(newsItemTpl %(u"我要找人抢台费", u"找球打，新玩法--抢台费", LOGO_IMG_URL, publishlink), newsItemTpl %(u"看看别人的抢台费", u"查看已有的约球信息", LOGO_IMG_URL, challlengelink))

def response_msg(request):
    msg = parse_msg(request)
    
    #response event message
    if msg['MsgType'] == "event":
        if msg['Event'] == 'subscribe' or msg['Event'] == 'scan':
            specialEvent = getSpecialEventItem(request, msg['CreateTime'])
            respTitle = u'欢迎您关注我为台球狂官方微信'
            respDesc = u'获取更多身边俱乐部信息，请访问：http://www.pktaiqiu.com，与我们更多互动，发送您的位置信息给我们，为您推荐身边的台球俱乐部。发送 ？，帮助，获取帮助手册。'
            response = newsItemTpl %(respTitle, respDesc, LOGO_IMG_URL, '')
            if specialEvent == None:
                echostr = newsReplyTpl %(msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 1, response)
            else:
                echostr = newsReplyTpl %(msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 1 + specialEvent[0], 
                        (specialEvent[1] + response))
               
            try:
                eventkey = msg['EventKey']
            except KeyError:
                eventkey = None
            recordUserActivity(msg['FromUserName'], 'event', msg['Event'], {'event': msg['Event'], 'eventkey': eventkey}, msg['CreateTime'], None)
            return echostr
        else:
            recordUserActivity(msg['FromUserName'], 'event', msg['Event'], {'event': msg['Event']}, msg['CreateTime'], None)
    #response location message
    elif msg['MsgType'] == "location":
        lat = msg['Location_X']
        lng = msg['Location_Y']
        baidu_loc = gcj2bd(float(lat),float(lng))
        baidu_loc_lat = unicode(baidu_loc[0])
        baidu_loc_lng = unicode(baidu_loc[1])
        nearbyPoolrooms = getNearbyPoolrooms(baidu_loc_lat, baidu_loc_lng, 3)[:1]
        specialEvent = getSpecialEventItem(request, msg['CreateTime'])
        eventCount = specialEvent[0] if specialEvent is not None else 0
        eventText = specialEvent[1] if specialEvent is not None else ''
        challengenews = getChallengeNews(request, msg, baidu_loc_lat, baidu_loc_lng)
        if len(nearbyPoolrooms) > 0:
            poolroom = nearbyPoolrooms[0]
            newsPoolroomText = getNewsPoolroomsText(request, nearbyPoolrooms)
            nativetime = datetime.utcfromtimestamp(float(msg['CreateTime']))
            localtz = pytz.timezone(settings.TIME_ZONE)
            localtime = localtz.localize(nativetime)
            coupons = poolroom.getCoupons(localtime)
            if coupons.count() > 0:
                echopictext = newsReplyTpl % (
                                 msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 1 + coupons.count() + eventCount + 2,
                                 eventText + newsPoolroomText + getCouponsText(request, coupons) + challengenews) 
            else:
                echopictext = newsReplyTpl % (
                         msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 1 + eventCount + 2,
                         eventText + newsPoolroomText + challengenews)
            recordUserActivity(msg['FromUserName'], 'location', poolroom.name, {'lat': lat, 'lng': lng, 'scale': msg['Scale'], 'label': ['Label']}, msg['CreateTime'], 
                               {'id': poolroom.id, 'name': poolroom.name, 'distance': poolroom.distance})
            return echopictext
        else:
            data = u"在您附近3公里以内，没有推荐的台球俱乐部，去其他地方试试吧"
            echostr = getNotFoundResponse(msg, specialEvent, data, 2, challengenews)
            recordUserActivity(msg['FromUserName'], 'location', '', {'lat': lat, 'lng': lng, 'scale': msg['Scale'], 'label': ['Label']}, msg['CreateTime'], 
                               None)
            return echostr
    #response voice message
    elif msg['MsgType'] == "voice":
        echostr = textReplyTpl % (
                             msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                             '语音信息回复敬请期待')
        return echostr
    #response image message
    elif msg['MsgType'] == "image":
        media_id = msg['MediaId']
        pic_url = msg['PicUrl']
        pics = set_pic(request)
        picid = randint(0,len(pics)-1)
        echostr = textReplyTpl % (
                             msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                             '图片信息回复敬请期待'+'\r\nmedia id is '+media_id)
        echopictext = newsReplyTpl % (
                            msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 1,
                            (newsItemTpl %('hello', 'hi', pic_url, '')))
        echopic = picReplyTpl % (
                            msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                            pics[picid])
        return echopic
    #response link message
    elif msg['MsgType'] == "link":
        echostr = textReplyTpl % (
                             msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                             '链接信息回复敬请期待')
        return echostr
    #response video message
    elif msg['MsgType'] == "video":
        media_id = msg['MediaId']
        echostr = textReplyTpl % (
                             msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                             '视频信息回复敬请期待'+'\r\nmedia id is:'+media_id)
        return echostr
    #response text message
    elif msg['MsgType'] == "text":
        def getCouponText(coupons, specialEvent = None):
            coupon = coupons[0]
            picurl = buildPoolroomImageURL(coupon.poolroom)
            weblink = buildAbsoluteURI(request, reverse('poolroom_detail', args=(coupon.poolroom.pk,)))
            echopictext = newsReplyTpl % (
                                        msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 2 + (specialEvent[0] if specialEvent != None else 0),
                                        (specialEvent[1] if specialEvent != None else '') + getCouponsText(request, (coupons)) + (newsItemTpl %(u"俱乐部详情", coupon.poolroom.name, picurl, weblink)))      
            return echopictext
        qqface = "/::\\)|/::~|/::B|/::\\||/:8-\\)|/::<|/::$|/::X|/::Z|/::'\\(|/::-\\||/::@|/::P|/::D|/::O|/::\\(|/::\\+|/:--b|/::Q|/::T|/:,@P|/:,@-D|/::d|/:,@o|/::g|/:\\|-\\)|/::!|/::L|/::>|/::,@|/:,@f|/::-S|/:\\?|/:,@x|/:,@@|/::8|/:,@!|/:!!!|/:xx|/:bye|/:wipe|/:dig|/:handclap|/:&-\\(|/:B-\\)|/:<@|/:@>|/::-O|/:>-\\||/:P-\\(|/::'\\||/:X-\\)|/::\\*|/:@x|/:8\\*|/:pd|/:<W>|/:beer|/:basketb|/:oo|/:coffee|/:eat|/:pig|/:rose|/:fade|/:showlove|/:heart|/:break|/:cake|/:li|/:bome|/:kn|/:footb|/:ladybug|/:shit|/:moon|/:sun|/:gift|/:hug|/:strong|/:weak|/:share|/:v|/:@\\)|/:jj|/:@@|/:bad|/:lvu|/:no|/:ok|/:love|/:<L>|/:jump|/:shake|/:<O>|/:circle|/:kotow|/:turn|/:skip|/:oY|/:#-0|/:hiphot|/:kiss|/:<&|/:&>"
        match = re.search(msg['Content'], qqface)
        content = set_content(request)
        if msg['Content'] in content.keys():
            echostr = textReplyTpl % (
                             msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                             content[msg['Content']])
            return echostr    
        elif match:
            echostr = textReplyTpl % (
                             msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                             msg['Content'])
            return echostr
        elif msg['Content'] == u"图片" or msg['Content'] == u"墙纸":
            pics = set_pic(request)
            picid = randint(0,len(pics)-1)
            echopic = picReplyTpl % (
                            msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                            pics[picid])
            return echopic
        elif msg['Content'] == u"花式" or msg['Content'] == u"花式台球":
            videos = set_video(request)
            videoid = randint(0,len(videos)-1)
            echopictext = newsReplyTpl % (
                             msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 1,
                             (newsItemTpl %(videos[videoid]['title'], videos[videoid]['description'], videos[videoid]['plink'], videos[videoid]['vlink'])))         
            return echopictext
        elif msg['Content'] == u"中式八球" or msg['Content'] == u"中式" or msg['Content'] == u"zsbq":
            videos = set_zsbq_video(request)
            videoid = randint(0,len(videos)-1)
            echopictext = newsReplyTpl % (
                             msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 1,
                             (newsItemTpl %(videos[videoid]['title'], videos[videoid]['description'], videos[videoid]['plink'], videos[videoid]['vlink'])))        
            return echopictext
        elif msg['Content'] == u"团购" or msg['Content'] == u"找便宜" or msg['Content'] == u"优惠":
            nativetime = datetime.utcfromtimestamp(float(msg['CreateTime']))
            localtz = pytz.timezone(settings.TIME_ZONE)
            localtime = localtz.localize(nativetime)
            coupon = Coupon.objects.filter(getCouponCriteria(localtime)).order_by('?')[:1]
            specialEvent = getSpecialEventItem(request, msg['CreateTime'])
            if len(coupon) > 0:
                recordUserActivity(msg['FromUserName'], 'text', 'coupon', {'content': msg['Content']}, msg['CreateTime'], 
                               {'count': len(coupon), 'coupon': True})
                return getCouponText(coupon, specialEvent)
            else:
                data = u'暂时没有俱乐部有"优惠"或"团购"。'
                echostr = getNotFoundResponse(msg, specialEvent, data)
                recordUserActivity(msg['FromUserName'], 'text', 'nocoupon', {'content': msg['Content']}, msg['CreateTime'], 
                               None)
                return echostr
        elif msg['Content'] == u"云川" or msg['Content'] == u"yunchuan" or msg['Content'] == u"yc":
            specialEvent = getSpecialEventItem(request, msg['CreateTime'])
            nativetime = datetime.utcfromtimestamp(float(msg['CreateTime']))
            localtz = pytz.timezone(settings.TIME_ZONE)
            localtime = localtz.localize(nativetime)
            coupon = Coupon.objects.filter(getCouponCriteria(localtime)).filter(poolroom__in=Poolroom.objects.filter(name__startswith=u'北京云川')).order_by('?')[:1]
            if len(coupon) > 0:
                recordUserActivity(msg['FromUserName'], 'text', 'yunchuan', {'content': msg['Content']}, msg['CreateTime'], 
                               {'count': len(coupon), 'yunchuan_coupon': True})
                return getCouponText(coupon, specialEvent)
            else:
                data = u'云川俱乐部暂没有优惠。请输入"优惠"或"团购“查找其他俱乐部的优惠。'
                echostr = getNotFoundResponse(msg, specialEvent, data)
                recordUserActivity(msg['FromUserName'], 'text', 'noyunchuan', {'content': msg['Content']}, msg['CreateTime'], 
                               None)
                return echostr
        elif msg['Content'] == u"活动":
            specialEvent = getSpecialEventItem(request, msg['CreateTime'])
            nativetime = datetime.utcfromtimestamp(float(msg['CreateTime']))
            localtz = pytz.timezone(settings.TIME_ZONE)
            starttime = localtz.localize(nativetime)
            acts, starttime, endtime = getMatchByRequest(request, starttime, deltadays=7)
            acts = acts.filter(type=2)
            count = acts.count()
            if count > 0:
                echopictext = getActNewsText(request, msg, acts, count, specialEvent)
                recordUserActivity(msg['FromUserName'], 'text', 'activity', {'content': msg['Content']}, msg['CreateTime'], 
                               {'count': count, 'activity': True})
                return echopictext
            else:
                data = u'最近7天内没有被收录的爱好者活动'
                echostr = getNotFoundResponse(msg, specialEvent, data)
                recordUserActivity(msg['FromUserName'], 'text', 'noactivity', {'content': msg['Content']}, msg['CreateTime'], 
                               None)
                return echostr
        elif msg['Content'] == u"比赛":
            specialEvent = getSpecialEventItem(request, msg['CreateTime'])
            eventCount = specialEvent[0] if specialEvent is not None else 0
            eventText = specialEvent[1] if specialEvent is not None else ''
            nativetime = datetime.utcfromtimestamp(float(msg['CreateTime']))
            localtz = pytz.timezone(settings.TIME_ZONE)
            starttime = localtz.localize(nativetime)
            matches, starttime, endtime = getMatchByRequest(request, starttime, deltadays=7)
            matches = matches.filter(type=1)
            count = matches.count()
            if count > 0:
                def getMatchesText(matches):
                    text = []
                    for match in matches:
                        picurl = buildPoolroomImageURL(match.poolroom)
                        text.append(newsItemTpl %(match.title, u"比赛开始时间: %s" %(getNativeTime(match.starttime)), picurl, buildAbsoluteURI(request, reverse('match_detail', args=(match.pk,)))))
                    return ''.join(text)
                matches = matches[:MAX_NEWSITEM - eventCount]
                echopictext = newsReplyTpl % (
                                 msg['FromUserName'], msg['ToUserName'], str(int(time.time())), len(matches) + eventCount,
                                  eventText + getMatchesText(matches))
                recordUserActivity(msg['FromUserName'], 'text', 'match', {'content': msg['Content']}, msg['CreateTime'], 
                               {'count': count, 'match': True})       
                return echopictext
            else:
                data = '最近7天内没有被收录的比赛'
                echostr = getNotFoundResponse(msg, specialEvent, data)
                recordUserActivity(msg['FromUserName'], 'text', 'nomatch', {'content': msg['Content']}, msg['CreateTime'], 
                               None)
                return echostr
        elif msg['Content'] in HELP_KEYWORDS:
            specialEvent = getSpecialEventItem(request, msg['CreateTime'])
            return newsReplyTpl %(msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 1 + specialEvent[0],
                                  specialEvent[1] + NEWS_HELP)
#         elif hasSpecialEvent(msg['CreateTime']) and msg['Content'] in CLUB_NAMES['22'] :
#             # like 'huiju' that is our partner
#             code, created = EventCode.objects.get_or_create(poolroom_id=22, event_id=1, userid=msg['FromUserName'])
#             if code != None:
#                 poolroom = Poolroom.objects.get(id=22)
#                 picurl = buildPoolroomImageURL(poolroom)
#                 originContent = buildAbsoluteURI(request, reverse('poolroom_detail', args=(poolroom.id,)))
#                 title = u'感谢你选择"%s"' %(poolroom.name)
#                 description = u"你的专属优惠码为'%s',可减免一小时台费，请在结账前出示。" %(code.chargecode)
#                 recordUserActivity(msg['FromUserName'], 'text', 'club_huiju', {'message': msg['Content']}, msg['CreateTime'], {'reply': description})
#                 return newsReplyTpl %(msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 1, 
#                         newsItemTpl %(title, description, picurl, originContent))
        elif (msg['Content'].startswith(u'慧聚验证') or msg['Content'].startswith(u'慧聚消费')):
            code = msg['Content'][4:]
            try:
                eventcode = EventCode.objects.get(chargecode=code, event_id=1, poolroom_id=22)
                if eventcode.used:
                    echostr = textReplyTpl % (msg['FromUserName'], msg['ToUserName'], str(int(time.time())), u'你提交消费码已使用')
                elif msg['Content'].startswith(u'慧聚验证'):
                    echostr = textReplyTpl % (msg['FromUserName'], msg['ToUserName'], str(int(time.time())), u'你提交的消费码正常，可以使用')
                elif msg['Content'].startswith(u'慧聚消费'):
                    eventcode.used = True
                    eventcode.usedtime = datetime.now()
                    eventcode.save()
                    recordUserActivity(msg['FromUserName'], 'text', 'club_huiju_charge', {'message': msg['Content']}, msg['CreateTime'], {'reply': 'charged'})
                    echostr = textReplyTpl % (msg['FromUserName'], msg['ToUserName'], str(int(time.time())), u'你提交的消费码正常，已记录为消费。请为持有者免1小时台费。')
            except EventCode.DoesNotExist:
                echostr = textReplyTpl % (msg['FromUserName'], msg['ToUserName'], str(int(time.time())), u'你提交的消费码不存在，请验证你的输入')
            return echostr
        else:
            specialEvent = getSpecialEventItem(request, msg['CreateTime'])
            if specialEvent == None:
                echostr = newsReplyTpl %(msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 1, NEWS_HELP)
                recordUserActivity(msg['FromUserName'], 'text', 'unknown', {'content': msg['Content']}, msg['CreateTime'], 
                                   None)
                return echostr
            else:
                echostr = newsReplyTpl %(msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 1 + specialEvent[0], 
                        (specialEvent[1] + NEWS_HELP))
                recordUserActivity(msg['FromUserName'], 'text', msg['Content'], {'content': msg['Content']}, msg['CreateTime'], 
                                   None)
                return echostr
    #response unsupported message
    else:
        echostr = newsReplyTpl %(msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 1, NEWS_HELP)
        return echostr
    
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

def buildAbsoluteURI(request, relativeURI):
    try:
        if 'pktaiqiu.com' in request.META['HTTP_HOST']:
            return set_query_parameter(request.build_absolute_uri(relativeURI), 'from', 'wechat')
    except KeyError:
        pass
    return set_query_parameter("http://www.pktaiqiu.com%s" %(relativeURI), 'from', 'wechat')

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

def getCouponsText(request, coupons):
    text = []
    for coupon in coupons:
        picurl = buildPoolroomImageURL(coupon.poolroom)
        couponurl = buildAbsoluteURI(request, reverse('coupontracker', args=(coupon.id,)))
        text.append(newsItemTpl %(coupon.title, coupon.description, picurl, couponurl))
    return ''.join(text)

@csrf_exempt
def weixin(request):
    if request.method=='GET':
        response=HttpResponse(checkSignature(request))
        return response
    elif request.method=='POST':
        return HttpResponse(response_msg(request),content_type="application/xml")
    else:
        return HttpResponse("hello world")

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
                & Q(keyword='subscribe')).distinct()
        
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
        messageEvents = WechatActivity.objects.filter(Q(receivedtime__gte=startdate) & Q(receivedtime__lt=enddate) & ~Q(eventtype='event'))
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
    
def response_msg_bj_university_association(request):
    msg = parse_msg(request)
    
    helpmsg = u"发送'俱乐部'或'球房'查找高校台球联盟的合作球房。发送'活动'获取一周内高校台球联盟活动详情。"
    echostr = None
    #response event message
    if msg['MsgType'] == "event":
        if msg['Event'] == 'subscribe' or msg['Event'] == 'scan':
            echostr = textReplyTpl % (
                    msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                    '欢迎您关注北京高校台球联盟微信。发送 ？，帮助，获取帮助手册。')
            try:
                eventkey = msg['EventKey']
            except KeyError:
                eventkey = None
            recordUserActivity(msg['FromUserName'], 'event', msg['Event'], {'event': msg['Event'], 'eventkey': eventkey}, msg['CreateTime'], None, 2)
        else:
            recordUserActivity(msg['FromUserName'], 'event', msg['Event'], {'event': msg['Event']}, msg['CreateTime'], None, 2)
    elif msg['MsgType'] == "text":
        if msg['Content'] == u"活动":
            nativetime = datetime.utcfromtimestamp(float(msg['CreateTime']))
            localtz = pytz.timezone(settings.TIME_ZONE)
            starttime = localtz.localize(nativetime)
            acts, starttime, endtime = getMatchByRequest(request, starttime, deltadays=7)
            acts = acts.filter(Q(type=2) & Q(organizer=2))
            count = acts.count()
            if count > 0:
                echostr = getActNewsText(request, msg, acts, count, None)
                recordUserActivity(msg['FromUserName'], 'text', 'activity', {'content': msg['Content']}, msg['CreateTime'], 
                               {'count': count, 'activity': True}, 2)
            else:
                data = u'最近7天内没有被收录的北京高校台球联盟活动'
                echostr = getNotFoundResponse(msg, None, data)
                recordUserActivity(msg['FromUserName'], 'text', 'noactivity', {'content': msg['Content']}, msg['CreateTime'], 
                               None, 2)
        elif msg['Content'] == u"俱乐部" or msg['Content'] == u"球房":
            poolrooms = Poolroom.objects.filter(poolroomuser__group=2).order_by('?')[:10]
            if len(poolrooms) > 0:
                echostr = newsReplyTpl % (
                    msg['FromUserName'], msg['ToUserName'], str(int(time.time())), poolrooms.count(), getNewsPoolroomsText(request, poolrooms))
                recordUserActivity(msg['FromUserName'], 'text', 'poolroom', {'content': msg['Content']}, msg['CreateTime'], 
                               {'count': len(poolrooms)}, 2)
            else:
                echostr = getNotFoundResponse(msg, None, u'暂时没有收录的北京高校台球联盟合作球房')
                recordUserActivity(msg['FromUserName'], 'text', 'nopoolroom', {'content': msg['Content']}, msg['CreateTime'], 
                               None, 2)
        elif msg['Content'] in HELP_KEYWORDS:
            echostr = textReplyTpl % (msg['FromUserName'], msg['ToUserName'], str(int(time.time())), helpmsg)
        else:
            recordUserActivity(msg['FromUserName'], 'text', 'unknown', {'content': msg['Content']}, msg['CreateTime'], None, 2)
    if echostr is None:
        echostr = textReplyTpl % (msg['FromUserName'], msg['ToUserName'], str(int(time.time())), '%s%s' %(u'感谢您发送的消息。', helpmsg))
    return echostr
        
@csrf_exempt
def bj_university_association(request):
    if request.method=='GET':
        response=HttpResponse(checkSignature(request, token='pktaiqiucom'))
        return response
    elif request.method=='POST':
        return HttpResponse(response_msg_bj_university_association(request),content_type="application/xml")