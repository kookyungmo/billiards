# coding=utf-8
from django.http import HttpResponse
import hashlib, time, re, json
from xml.etree import ElementTree as ET
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext, Template
from django.utils.encoding import smart_str, smart_unicode
from billiards.views.poolroom import nearby
from billiards.location_convertor import gcj2bd
from random import randint
import urllib2, urllib

def checkSignature(request):
    signature=request.GET.get('signature','')
    timestamp=request.GET.get('timestamp','')
    nonce=request.GET.get('nonce','')
    echostr=request.GET.get('echostr','')
    #这里的token我放在setting，可以根据自己需求修改
    token="pktaiqiu"

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
      "fj":"您想找附近的台球俱乐部吗？请发送您的位置给我们，给您推荐身边的台球俱乐部。",
      "bs":"您想找台球俱乐部举办的比赛吗？",
      "nh":"你好啊，朋友",
      "bz":"您好，需要帮助吗？\r\n1、发送您的位置信息，获取附近台球俱乐部信息。\r\n2、发送“中式八球”，“花式台球”获取我们精选的台球视频集锦。\r\n3、发送相片，图片，一起和身边的朋友们交换互动。",
      "zf":"送祝福啦，祝您马年吉祥，身体健康，马到成功，财源滚滚来！",
      "help":"您好，需要帮助吗？\r\n1、发送您的位置信息，获取附近台球俱乐部信息。\r\n2、发送“中式八球”，“花式台球”获取我们精选的台球视频集锦。\r\n3、发送相片，图片，一起和身边的朋友们交换互动。",
      "yeah":"oh,yeah,我们一起为您欢呼",

      #Chinese content
      u"你好":"你好啊，朋友",
      u"附近":"您想找附近的台球俱乐部吗？请发送您的位置给我们，给您推荐身边的台球俱乐部。",
      u"早上好":"给您请早儿了",
      u"吃了吗":"劳您费心了，我吃了",
      u"新年好":"新年好呀，新年好呀，祝您和家人新年好，身体健康，万事如意",
      u"新年快乐":"祝您马年马到成功，吉祥如意，吉星高照，大吉大利",
      u"春节快乐":"祝您马年马到成功，吉祥如意，吉星高照，大吉大利",
      u"呵呵":"笑一笑十年少",
      u"再见":"您走好，欢迎随时找我来聊聊",
      u"帮助":"您好，需要帮助吗？\r\n1、发送您的位置信息，获取附近台球俱乐部信息。\r\n2、发送“中式八球”，“花式台球”获取我们精选的台球视频集锦。\r\n3、发送相片，图片，一起和身边的朋友们交换互动。",
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

      #face mark
      #"/::)":"/:,@-D",
      #marks
      "?":"您好，需要帮助吗？\r\n1、发送您的位置信息，获取附近台球俱乐部信息。\r\n2、发送“中式八球”，“花式台球”获取我们精选的台球视频集锦。\r\n3、发送相片，图片，一起和身边的朋友们交换互动。",
      u"？":"您好，需要帮助吗？\r\n1、发送您的位置信息，获取附近台球俱乐部信息。\r\n2、发送“中式八球”，“花式台球”获取我们精选的台球视频集锦。\r\n3、发送相片，图片，一起和身边的朋友们交换互动。"
}
    return content

def json_parse(url):
    data = urllib2.urlopen(url).read()
    j_data = json.loads(data)
    #j_dump_data = json.dumps(j_data, ensure_ascii=False)
    return j_data
  
def response_msg(request):
    msg = parse_msg(request)
    #handle text message
    textTpl = """<xml>
             <ToUserName><![CDATA[%s]]></ToUserName>
             <FromUserName><![CDATA[%s]]></FromUserName>
             <CreateTime>%s</CreateTime>
             <MsgType><![CDATA[text]]></MsgType>
             <Content><![CDATA[%s]]></Content>
             <FuncFlag>0</FuncFlag>
             </xml>"""
    #handle event message
    eventTpl = """<xml>
             <ToUserName><![CDATA[%s]]></ToUserName>
             <FromUserName><![CDATA[%s]]></FromUserName>
             <CreateTime>%s</CreateTime>
             <MsgType><![CDATA[event]]></MsgType>
             <Event><![CDATA[%s]]></Event>
             </xml>"""
    #handle location message
    locationTpl = """<xml>
             <ToUserName><![CDATA[%s]]></ToUserName>
             <FromUserName><![CDATA[%s]]></FromUserName>
             <CreateTime>%s</CreateTime>
             <MsgType><![CDATA[location]]></MsgType>
             <Location_X>%s</Location_X>
             <Location_Y>%s</Location_Y>
             <Scale>20</Scale>
             <Label><![CDATA[位置信息]]></Label>
             <MsgId>1234567890123456</MsgId>
             </xml> """
    #handle picture message
    picTpl = """ <xml>
             <ToUserName><![CDATA[%s]]></ToUserName>
             <FromUserName><![CDATA[%s]]></FromUserName>
             <CreateTime>%s</CreateTime>
             <MsgType><![CDATA[image]]></MsgType>
             <PicUrl><![CDATA[this is url]]></PicUrl>
             <MediaId><![CDATA[%s]]></MediaId>
             <MsgId>1234567890123456</MsgId>
             </xml>"""
    picRpl = """<xml>
             <ToUserName><![CDATA[%s]]></ToUserName>
             <FromUserName><![CDATA[%s]]></FromUserName>
             <CreateTime>%s</CreateTime>
             <MsgType><![CDATA[image]]></MsgType>
             <Image>
             <MediaId><![CDATA[%s]]></MediaId>
             </Image>
             </xml>"""
    #handle voice message
    voiceTpl = """<xml>
             <ToUserName><![CDATA[%s]]></ToUserName>
             <FromUserName><![CDATA[%s]]></FromUserName>
             <CreateTime>%s</CreateTime>
             <MsgType><![CDATA[voice]]></MsgType>
             <MediaId><![CDATA[media_id]]></MediaId>
             <Format><![CDATA[Format]]></Format>
             <MsgId>1234567890123456</MsgId>
             </xml>"""
    #handle video message
    videoTpl = """<xml>
             <ToUserName><![CDATA[%s]]></ToUserName>
             <FromUserName><![CDATA[%s]]></FromUserName>
             <CreateTime>%s</CreateTime>
             <MsgType><![CDATA[video]]></MsgType>
             <MediaId><![CDATA[%s]]></MediaId>
             <ThumbMediaId><![CDATA[thumb_media_id]]></ThumbMediaId>
             <MsgId>1234567890123456</MsgId>
             </xml>"""
    videoRpl = """<xml>
             <ToUserName><![CDATA[%s]]></ToUserName>
             <FromUserName><![CDATA[%s]]></FromUserName>
             <CreateTime>%s</CreateTime>
             <MsgType><![CDATA[video]]></MsgType>
             <Video>
             <MediaId><![CDATA[%s]]></MediaId>
             <Title><![CDATA[%s]]></Title>
             <Description><![CDATA[%s]]></Description>
             </Video> 
             </xml>"""
    #handle link message
    linkTpl = """<xml>
             <ToUserName><![CDATA[%s]]></ToUserName>
             <FromUserName><![CDATA[%s]]></FromUserName>
             <CreateTime>%s</CreateTime>
             <MsgType><![CDATA[link]]></MsgType>
             <Title><![CDATA[公众平台官网链接]]></Title>
             <Description><![CDATA[公众平台官网链接]]></Description>
             <Url><![CDATA[url]]></Url>
             <MsgId>1234567890123456</MsgId>
             </xml> """
    #handle pic & text message
    pictextTpl = """<xml>
             <ToUserName><![CDATA[%s]]></ToUserName>
             <FromUserName><![CDATA[%s]]></FromUserName>
             <CreateTime>%s</CreateTime>
             <MsgType><![CDATA[news]]></MsgType>
             <ArticleCount>1</ArticleCount>
             <Articles>
             <item>
             <Title><![CDATA[%s]]></Title> 
             <Description><![CDATA[%s]]></Description>
             <PicUrl><![CDATA[%s]]></PicUrl>
             <Url><![CDATA[%s]]></Url>
             </item>
             </Articles>
             </xml>""" 

    pictext2Tpl = """<xml>
             <ToUserName><![CDATA[%s]]></ToUserName>
             <FromUserName><![CDATA[%s]]></FromUserName>
             <CreateTime>%s</CreateTime>
             <MsgType><![CDATA[news]]></MsgType>
             <ArticleCount>2</ArticleCount>
             <Articles>
             <item>
             <Title><![CDATA[%s]]></Title> 
             <Description><![CDATA[%s]]></Description>
             <PicUrl><![CDATA[%s]]></PicUrl>
             <Url><![CDATA[%s]]></Url>
             </item>
             <item>
             <Title><![CDATA[%s]]></Title> 
             <Description><![CDATA[%s]]></Description>
             <PicUrl><![CDATA[%s]]></PicUrl>
             <Url><![CDATA[%s]]></Url>
             </item>
             </Articles>
             </xml>""" 
    
    content = set_content(request)
    #response event message
    if msg['MsgType'] == "event":
      echostr = textTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           '欢迎您关注我为台球狂官方微信，获取更多身边俱乐部信息，请访问：http://www.pktaiqiu.com，与我们更多互动，发送您的位置信息给我们，为您推荐身边的台球俱乐部。发送 ？，帮助，获取帮助手册。')
      return echostr
    #response location message
    elif msg['MsgType'] == "location":
      lat = msg['Location_X']
      lng = msg['Location_Y']
      baidu_loc = gcj2bd(float(lat),float(lng))
      baidu_loc_lat = unicode(baidu_loc[0])
      baidu_loc_lng = unicode(baidu_loc[1])
      url = "http://www.pktaiqiu.com/poolroom/nearby/"+baidu_loc_lat+","+baidu_loc_lng+"/3"
      raw_data = json_parse(url)

      if len(raw_data) != 0:
          club = raw_data[0]['fields']['name']
          address = raw_data[0]['fields']['address']
          tel = raw_data[0]['fields']['tel']
          size = unicode(raw_data[0]['fields']['size'])
          lng_baidu = raw_data[0]['fields']['lng_baidu']
          lat_baidu = raw_data[0]['fields']['lat_baidu']
          pkid = unicode(raw_data[0]['pk'])
          businesshours = raw_data[0]['fields']['businesshours']
          picurl = "http://api.map.baidu.com/staticimage?center="+lng_baidu+","+lat_baidu+"&width=450&height=300&zoom=18&scale=2&markers="+lng_baidu+","+lat_baidu+"&markerStyles=-1,"+"http://billiardsalbum.bcs.duapp.com/2014/01/marker-2.png"
          originContent = "http://www.pktaiqiu.com/poolroom/"+pkid
          title = club
          discription = "地址："+address+"\r\n营业面积："+size+"平方米"+"\r\n营业时间："+businesshours+"\r\n电话："+tel
          data = "附近精选台球俱乐部：\r\n"+club+"\r\n地址："+address+"\r\n营业面积："+size+"平方米"+"\r\n营业时间："+businesshours+"\r\n电话："+tel
          echopictext = pictextTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           title, discription, picurl, originContent)
          return echopictext
      else:
          data = "在您附近，没有推荐的台球俱乐部，去其他地方试试吧"
          echostr = textTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           data)
          return echostr
    #response voice message
    elif msg['MsgType'] == "voice":
      echostr = textTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           '语音信息回复敬请期待')
      return echostr
    #response image message
    elif msg['MsgType'] == "image":
      media_id = msg['MediaId']
      pic_url = msg['PicUrl']
      pics = set_pic(request)
      picid = randint(0,len(pics)-1)
      echostr = textTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           '图片信息回复敬请期待'+'\r\nmedia id is '+media_id)
      echopictext = pictextTpl % (
                          msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                          'hello', 'hi', pic_url, '')
      echopic = picRpl % (
                          msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                          pics[picid])
      return echopic
    #response link message
    elif msg['MsgType'] == "link":
      echostr = textTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           '链接信息回复敬请期待')
      return echostr
    #response video message
    elif msg['MsgType'] == "video":
      media_id = msg['MediaId']
      echostr = textTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           '视频信息回复敬请期待'+'\r\nmedia id is:'+media_id)
      echovideo = videoRpl % (msg['FromUserName'], msg['ToUserName'], str(int(time.time())),'sXzKe8DDiDtNMdxgg-76VBC_BlKEDZ3qwVO1Qqw9BqN_m97Er_I2hFCDYcSflodh','','')
      return echostr
    #response text message
    elif msg['MsgType'] == "text":
        qqface = "/::\\)|/::~|/::B|/::\\||/:8-\\)|/::<|/::$|/::X|/::Z|/::'\\(|/::-\\||/::@|/::P|/::D|/::O|/::\\(|/::\\+|/:--b|/::Q|/::T|/:,@P|/:,@-D|/::d|/:,@o|/::g|/:\\|-\\)|/::!|/::L|/::>|/::,@|/:,@f|/::-S|/:\\?|/:,@x|/:,@@|/::8|/:,@!|/:!!!|/:xx|/:bye|/:wipe|/:dig|/:handclap|/:&-\\(|/:B-\\)|/:<@|/:@>|/::-O|/:>-\\||/:P-\\(|/::'\\||/:X-\\)|/::\\*|/:@x|/:8\\*|/:pd|/:<W>|/:beer|/:basketb|/:oo|/:coffee|/:eat|/:pig|/:rose|/:fade|/:showlove|/:heart|/:break|/:cake|/:li|/:bome|/:kn|/:footb|/:ladybug|/:shit|/:moon|/:sun|/:gift|/:hug|/:strong|/:weak|/:share|/:v|/:@\\)|/:jj|/:@@|/:bad|/:lvu|/:no|/:ok|/:love|/:<L>|/:jump|/:shake|/:<O>|/:circle|/:kotow|/:turn|/:skip|/:oY|/:#-0|/:hiphot|/:kiss|/:<&|/:&>"
        match = re.search(msg['Content'], qqface)       
        if msg['Content'] in content.keys():
          echostr = textTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           content[msg['Content']])
          return echostr    
        elif match:
          echostr = textTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           msg['Content'])
          return echostr
        elif msg['Content'] == "图片" or msg['Content'] == "墙纸":
          pics = set_pic(request)
          picid = randint(0,len(pics)-1)
          echopic = picRpl % (
                          msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                          pics[picid])
          return echopic
        elif msg['Content'] == "花式" or msg['Content'] == "花式台球":
          videos = set_video(request)
          videoid = randint(0,len(videos)-1)
          echopictext = pictextTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           videos[videoid]['title'], videos[videoid]['description'], videos[videoid]['plink'], videos[videoid]['vlink'])          
          return echopictext
        elif msg['Content'] == "中式八球" or msg['Content'] == "中式" or msg['Content'] == "zsbq":
          videos = set_zsbq_video(request)
          videoid = randint(0,len(videos)-1)
          echopictext = pictextTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           videos[videoid]['title'], videos[videoid]['description'], videos[videoid]['plink'], videos[videoid]['vlink'])          
          return echopictext
        else:
          replywords = msg['Content']
          echostr = textTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           '我们无法正确解析您发送来的信息：“'+replywords+'“，请发送您的位置，获取身边俱乐部信息')
          return echostr
    #response unsupported message
    else:
      echostr = textTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           '您发送的内容我们无法识别，请发送其他类型的消息')
      return echostr


@csrf_exempt
def weixin(request):
    if request.method=='GET':
        response=HttpResponse(checkSignature(request))
        return response
    elif request.method=='POST':
        xmlstr = smart_str(request.body)
        return HttpResponse(response_msg(request),content_type="application/xml")
    else:
        return HttpResponse("hello world")





