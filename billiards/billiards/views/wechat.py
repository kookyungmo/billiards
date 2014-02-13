# coding=utf-8
from django.http import HttpResponse
import hashlib, time, re, json
from xml.etree import ElementTree as ET
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext, Template
from django.utils.encoding import smart_str, smart_unicode
from billiards.views.poolroom import nearby
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
      
def set_content(request):
    content = {
      #English content
      "hi":"Hello",
      "fj":"您想找附近的台球俱乐部吗？",
      "bs":"您想找台球俱乐部举办的比赛吗？",
      "nh":"你好啊，朋友",
      "bz":"帮助信息",
      "zf":"送祝福啦，祝您马年吉祥，身体健康，马到成功，财源滚滚来！",
      "help":"您好，需要帮助吗？\r\n1、发送中文或者词语拼音首字母，聊天机器人陪您聊天解闷。\r\n2、发送您的位置信息，获取附近台球俱乐部信息。",
      #Chinese content
      u"你好":"你好啊，朋友",
      u"早上好":"给您请早儿了",
      u"吃了吗":"劳您费心了，我吃了",
      u"新年好":"新年好呀，新年好呀，祝您和家人新年好，身体健康，万事如意",
      u"呵呵":"笑一笑十年少",
      u"再见":"您走好，欢迎随时找我来聊聊",
      u"帮助":"您好，需要帮助吗？\r\n1、发送中文或者词语拼音首字母，聊天机器人陪您聊天解闷。\r\n2、发送您的位置信息，获取附近台球俱乐部信息。",
      #face mark
      #"[微笑]":"[愉快]"
      #marks
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
             <PicUrl><![CDATA[this is a url]]></PicUrl>
             <MediaId><![CDATA[media_id]]></MediaId>
             <MsgId>1234567890123456</MsgId>
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
             <MediaId><![CDATA[media_id]]></MediaId>
             <ThumbMediaId><![CDATA[thumb_media_id]]></ThumbMediaId>
             <MsgId>1234567890123456</MsgId>
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
   
    content = set_content(request)
    #response event message
    if msg['MsgType'] == "event":
      echostr = textTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           '欢迎您关注我为台球狂官方微信，获取更多身边俱乐部信息，请访问：http://www.pktaiqiu.com，想与我们更多互动，发送您想说的话给我们吧')
      return echostr
    #response location message
    elif msg['MsgType'] == "location":
      lat = msg['Location_X']
      lng = msg['Location_Y']
      url = "http://www.pktaiqiu.com/poolroom/nearby/"+lat+','+lng+"/3"
      raw_data = json_parse(url)
      if len(raw_data) != 0:
          data = "您的附近有一家名为\"" + raw_data[0]['fields']['name'] + "\"的台球俱乐部\r\n" + "地址：" + raw_data[0]['fields']['address'] + "\r\n" + "前台电话：" + raw_data[0]['fields']['tel']
          data_lat = raw_data[0]['fields']['lat_baidu']
          data_lng = raw_data[0]['fields']['lng_baidu']
      else:
          data = "您的附近没有台球俱乐部，去其他地方找找看吧"
      echostr = textTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           data)
      return echostr
    #response voice message
    elif msg['MsgType'] == "voice":
      echostr = textTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           '这是一条语音信息')
      return echostr
    #response image message
    elif msg['MsgType'] == "image":
      echostr = textTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           '这是一条图片信息')
      return echostr
    #response link message
    elif msg['MsgType'] == "link":
      echostr = textTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           '这是一条链接信息')
      return echostr
    #response video message
    elif msg['MsgType'] == "video":
      echostr = textTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           '这是一条视频信息')
      return echostr
    #response text message
    elif msg['MsgType'] == "text":
        if msg['Content'] in content.keys():
          echostr = textTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           content[msg['Content']])
          return echostr    
        else:
          echostr = textTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           '您输入的文字信息不在我们的信息库里,请输入单词拼音的首字母，或者您还可以发送文字，语音，图片，视频，位置与我们一起互动')
          return echostr
    #response unsupported message
    else:
      echostr = textTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           '您发送的内容我们无法识别')
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

