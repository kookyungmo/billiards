# coding=utf-8
from django.http import HttpResponse
import hashlib, time, re, json
from xml.etree import ElementTree as ET
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext, Template
from django.utils.encoding import smart_str, smart_unicode
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
  
def set_match(request):
    matches = [
               {"title":"2014-02-13 北京高谷台球俱乐部宣武门店，冠军：300现金+100储值卡","link":"http://www.pktaiqiu.com/match/75/"}
               ]
    return matches
  
def set_act(request):
    acts = [
               {"title":"2014-02-10 北京高校台球联盟群活动","detail":"北京领航者台球俱乐部","picurl":"http://billiardsalbum.bcs.duapp.com/2014/02/bjgxtqlm.jpg","link":"http://www.pktaiqiu.com/match/82/"},
               {"title":"2014-02-10 天天夜时尚，夜夜玩到底","detail":"北京夜时尚护国寺店\r\n地址：北京市西城区护国寺大街137号泊鑫宾馆地下一层\r\n电话：010-52427963","picurl":"http://billiardsalbum.bcs.duapp.com/resources/poolroom/f3100fe948a1ff838b63d50fbb11b9_IMG_1109.JPG","link":"http://www.pktaiqiu.com/match/73/"}    
               ]
    return acts
  
def set_yunchuan_coupon(request):
    yunchuan_coupons = [
                        {"pk":"107", "title":"团购：北京云川台球俱乐部志新桥店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9903301", "baidu_lng":"116.3757489", "tel":"010-62018887 ", "address":"北京海淀区北四环志新桥向南200米路西 ", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"171", "title":"团购：北京云川台球俱乐部方庄店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.8721039", "baidu_lng":"116.4421229", "tel":"010-67622828", "address":"北京市丰台区蒲方路1号", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"113", "title":"团购：北京云川台球俱乐部三里屯店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9335159", "baidu_lng":"116.4625773", "tel":"010-68085558", "address":"北京市朝阳区三里屯南路16号泰悦豪庭B1楼", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"105", "title":"团购：北京云川台球俱乐部永定门店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.8709788", "baidu_lng":"116.4130107", "tel":"010-87893336 ", "address":"北京永定门外安乐林路天天家园小区内东侧 ", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"109", "title":"团购：北京云川台球俱乐部右安门店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.8658325", "baidu_lng":"116.3708853", "tel":"010-83527770 ", "address":"北京丰台区右安门外大街99号", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"172", "title":"团购：北京云川台球俱乐部西四店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9406734", "baidu_lng":"116.3858051", "tel":"010-66166490", "address":"北京市西城区西四北大街乙158号地下一层", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"173", "title":"团购：北京云川台球俱乐部保福寺店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9861512", "baidu_lng":"116.3339893", "tel":"010-62566598", "address":"北京市海淀区中关村南三街文化体育中心2层", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"174", "title":"团购：北京云川台球俱乐部马甸店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9881982", "baidu_lng":"116.3871993", "tel":"010-62379990", "address":"北京市朝阳区华严北里甲一号", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"175", "title":"团购：北京云川台球俱乐部五道口店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9991614", "baidu_lng":"116.3465476", "tel":"010-82386906", "address":"北京市海淀区成府路23号五道口宾馆", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"176", "title":"团购：北京云川台球俱乐部定慧桥店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9352214", "baidu_lng":"116.2687430", "tel":"010-58970485", "address":"北京市海淀区永定路乙1号院14楼2门地下1层（乐府江南小区门口）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"177", "title":"团购：北京云川台球俱乐部五棵松店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9068005", "baidu_lng":"116.2879723", "tel":"010-52126635", "address":"北京市海淀区今日家园8号地下一层", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"178", "title":"团购：北京云川台球俱乐部朝阳路店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9230932", "baidu_lng":"116.5330900", "tel":"010-65104646", "address":"北京市朝阳区朝阳路世纪天乐潮青汇商场5层", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"179", "title":"团购：北京云川台球俱乐部六里桥店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.8880627", "baidu_lng":"116.3228218", "tel":"010-63333884", "address":"北京市丰台区太平桥西路华源1街4号楼（青年餐厅地下1层）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"180", "title":"团购：北京云川台球俱乐部酒仙桥店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9810040", "baidu_lng":"116.4969695", "tel":"010-64369489", "address":"北京市朝阳区酒仙桥路甲12号电子城科技大厦地下2层（临近比格餐厅）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"181", "title":"团购：北京云川台球俱乐部远洋山水店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9095537", "baidu_lng":"116.2467660", "tel":"010-88697183", "address":"北京市石景山区鲁谷东大街（远洋山水小区西门）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"182", "title":"团购：北京云川台球俱乐部岳各庄店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.8669009", "baidu_lng":"116.2657588", "tel":"010-63871652", "address":"北京市丰台区五里店卢沟桥路和光里小区2号楼地下1层（临近岳各庄检测场）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"183", "title":"团购：北京云川台球俱乐部将台路店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9721626", "baidu_lng":"116.5093368", "tel":"010-84598422", "address":"北京市朝阳区酒仙桥驼房营西里甲5号2楼云顶时尚台球俱乐部（临近乐食尚餐厅）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"184", "title":"团购：北京云川台球俱乐部良乡店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.7415050", "baidu_lng":"116.1481470", "tel":"010-69365789", "address":"北京市房山区良乡拱辰大街49号（科豪大厦4层）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"185", "title":"团购：北京云川台球俱乐部学知桥店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9796657", "baidu_lng":"116.3547898", "tel":"010-82050295", "address":"北京市海淀区知春路太月园3号楼地下一层", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"186", "title":"团购：北京云川台球俱乐部草桥店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.8515247", "baidu_lng":"116.3702949", "tel":"010-51471999", "address":"北京市丰台区北甲地路10号院三层", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"187", "title":"团购：北京云川台球俱乐部大屯店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"", "baidu_lng":"40.0093974", "tel":"116.4153867", "address":"北京市朝阳区亚运村安立路66号安立花园1号楼", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"188", "title":"团购：北京云川台球俱乐部新街口店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9444717", "baidu_lng":"116.3737303", "tel":"010-66537177", "address":"北京市西城区西直门内赵登禹路冠英园西区20楼B1楼(近地铁4号线新街口站D口)", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"189", "title":"团购：北京云川台球俱乐部交大店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9557359", "baidu_lng":"116.3543208", "tel":"010-82164788", "address":"北京市海淀区交大东路25号", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"190", "title":"团购：北京云川台球俱乐部白纸坊店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.8828696", "baidu_lng":"116.3533838", "tel":"010-63388918", "address":"北京市丰台区鸭子桥路信德园小区5-7（临近农业银行）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"191", "title":"团购：北京云川台球俱乐部花园桥店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9381604", "baidu_lng":"116.2958428", "tel":"010-88138880", "address":"北京市海淀区八里庄北里23号楼2层（临近碧水云天洗浴中心）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"192", "title":"团购：北京云川台球俱乐部丰体店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.8580647", "baidu_lng":"116.2928752", "tel":"010-63865550", "address":"北京市丰台区文体路58号（丰体工人俱乐部地下2层）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"193", "title":"团购：北京云川台球俱乐部鲁谷店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9078076", "baidu_lng":"116.2467837", "tel":"010-88697770", "address":"北京市石景山区雕塑园南街29号楼远洋山水小区东门（远洋山水售楼处地下1层）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"194", "title":"团购：北京云川台球俱乐部成寿寺店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.8596740", "baidu_lng":"116.4446929", "tel":"010-51228316", "address":"北京市丰台区方庄南路9号院方庄桥南300米（谱田大厦B1层）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"195", "title":"团购：北京云川台球俱乐部石佛营店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9351938", "baidu_lng":"116.5114810", "tel":"010-85819589", "address":"北京市朝阳区石佛营炫特区西门商业楼3层（临近卜蜂莲花超市）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"196", "title":"团购：北京云川台球俱乐部正阳桥店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.8559464", "baidu_lng":"116.2941854", "tel":"010-63833680转0", "address":"北京市丰台区正阳大街正阳北里18号楼底商1层（临近北京国阳医院）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"197", "title":"团购：北京云川台球俱乐部四惠店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9176263", "baidu_lng":"116.5012654", "tel":"010-85865147", "address":"北京市朝阳区八里庄西里75号楼远洋天地小区南门（临近四惠地铁站D口）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"198", "title":"团购：北京云川台球俱乐部广外店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.8923402", "baidu_lng":"116.3462058", "tel":"010-63334440", "address":"北京市西城区宣武门广安门外红居街5号楼", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"199", "title":"团购：北京云川台球俱乐部丰台东路店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.8543703", "baidu_lng":"116.3225823", "tel":"010-83619585", "address":"北京市丰台区丰台东路樊家村甲3号", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"200", "title":"团购：北京云川台球俱乐部马家堡店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.8437473", "baidu_lng":"116.3711004", "tel":"010-67570773", "address":"北京市丰台区马家堡嘉园路星河苑小区西门（安太妇产医院对面）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"201", "title":"团购：北京云川台球俱乐部九州店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9568581", "baidu_lng":"116.2797742", "tel":"010-88498575", "address":"北京市海淀区西四环北路71号郦城A区3号楼地下一层", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        {"pk":"202", "title":"团购：北京云川台球俱乐部望京店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9925667", "baidu_lng":"116.4852965", "tel":"010-64773066", "address":"北京市朝阳区广顺大街19号院会所（临近新世界百货）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
                        ]
    return yunchuan_coupons
  
def set_coupon(request):
    coupons = [
               {"pk":"25", "title":"团购：北京迈8赫台球会所, 17.8元，畅打两小时", "description":"17.8元，畅打两小时", "time":"2013年9月7日 至 2014年3月6日", "baidu_lat":"40.0135572", "baidu_lng":"116.4147791", "tel":"010-84802532", "address":"朝阳区安立路九台2000家园地下一层", "link":"http://bj.meituan.com/deal/9340453.html"},
               {"pk":"70", "title":"团购：北京隆轩台球俱乐部（望京）, 19.9元，畅打两小时", "description":"19.9元，畅打两小时", "time":"2013.10.19 至 2014.7.17", "baidu_lat":"39.9849635", "baidu_lng":"116.4750495", "tel":"010-64728646", "address":"北京望京花家地南里5号", "link":"http://bj.meituan.com/deal/7191716.html"},
               {"pk":"95", "title":"团购：北京堂棒棒台球（朝外大街）, 30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013.11.19 至 2014.2.18", "baidu_lat":"39.9257578", "baidu_lng":"116.4492575", "tel":"010-85694103", "address":"北京朝阳区日坛北路17号日坛国际贸易中心地下一层商业街星光大道北B088", "link":"http://bj.meituan.com/deal/8060768.html"},
               {"pk":"54", "title":"团购：北京七星岛8号台球俱乐部（牡丹园/北太平庄），38元，畅打三小时", "description":"38元，畅打三小时", "time":"2014.1.6 至 2014.7.5", "baidu_lat":"39.9836187", "baidu_lng":"116.3743070", "tel":"15701004091", "address":"北京海淀区牡丹园翠微商场院内", "link":"http://bj.meituan.com/deal/9362028.html"},
               {"pk":"92", "title":"团购：北京远望谷台球会所（紫竹桥），22元，畅打三小时", "description":"22元，畅打三小时", "time":"2013.11.13 至 2014.11.12", "baidu_lat":"39.9454621", "baidu_lng":"116.3203192", "tel":"010-62651088", "address":"北京海淀区西三环北路50号豪柏大厦C2座1-103室（紫竹桥东南角）", "link":"http://bj.meituan.com/deal/3654399.html"},
               {"pk":"55", "title":"团购：北京奥亨台球（草桥/公益西桥），18元，畅打三小时", "description":"18元，畅打三小时", "time":"2013.8.20 至 2014.2.19", "baidu_lat":"39.8438451", "baidu_lng":"116.3769232", "tel":"010-67529905", "address":"北京丰台区马家堡西路星河苑2号院22号楼地下一层", "link":"http://bj.meituan.com/deal/7737048.html"},
               {"pk":"30", "title":"团购：北京海格台球俱乐部（宣武门），19元，畅打两小时", "description":"19元，畅打两小时", "time":"2013.9.5 至 2014.3.31", "baidu_lat":"39.9009997", "baidu_lng":"116.3816211", "tel":"010-63183990", "address":"北京西城区宣武门外大街20号海格国际酒店地下2层", "link":"http://bj.meituan.com/deal/4211247.html"},
               {"pk":"28", "title":"团购：北京潘晓婷台球俱乐部（潘家园），19.8元，畅打两小时", "description":"19.8元，畅打两小时", "time":"2013年10月22日-2014年03月12日", "baidu_lat":"39.8752954", "baidu_lng":"116.4658044", "tel":"010-65305655 & 010-67628288", "address":"北京朝阳区东三环南路辅路联合国际大厦地下一层", "link":"http://bj.nuomi.com/deal/obyoqflp.html"},
               {"pk":"40", "title":"团购：北京球动力台球连锁俱乐部（立水桥），28.8元，畅打三小时", "description":"28.8元，畅打三小时", "time":"2013年11月20日至2014年02月20日", "baidu_lat":"40.0639378", "baidu_lng":"116.4217211", "tel":"010-57733777", "address":"北京昌平区立水桥明珠奥特莱斯中心广场地下一层 ", "link":"http://bj.nuomi.com/deal/fez5n2em.html"},
               {"pk":"34", "title":"团购：北京领航者台球俱乐部（菜市口），17.9元，畅打一小时", "description":"17.9元，畅打一小时", "time":"2013年10月22日-2014年03月03日", "baidu_lat":"39.8885423", "baidu_lng":"116.3994264", "tel":"010-63013337", "address":"北京西城区东经路禄长街2条2号（速8天桥店B一层）", "link":"http://bj.nuomi.com/deal/7xqwdcl7.html"},
               {"pk":"48", "title":"团购：北京昊天台球俱乐部（虎坊桥），19元，畅打两小时", "description":"19元，畅打两小时", "time":"2013年10月14日-2014年06月30日 ", "baidu_lat":"39.8896118", "baidu_lng":"116.3893745", "tel":"010-56155999", "address":"北京西城区虎坊路陶然北岸160-4号(近清华池)", "link":"http://bj.nuomi.com/deal/wt357lru.html"},
               {"pk":"42", "title":"团购：北京寻梦港台球俱乐部（回龙观），35元，畅打两小时", "description":"35元，畅打两小时", "time":"2013年10月29日至2014年03月05日", "baidu_lat":"40.0847300", "baidu_lng":"116.3392966", "tel":"13601248756", "address":"北京昌平区回龙观镇回龙观西大街18号2段1层", "link":"http://bj.nuomi.com/deal/esp4nfrt.html"},
               {"pk":"58", "title":"团购：北京猫头鹰台球俱乐部（酒仙桥），18.8元，畅打两小时", "description":"18.8元，畅打两小时", "time":"2013年10月18日-2014年04月15日", "baidu_lat":"39.9722142", "baidu_lng":"116.4973278", "tel":"010-51306858", "address":"北京朝阳区酒仙桥路26号晶都国际酒店B1楼", "link":"http://beijing.55tuan.com/goods-6a17a8a990c5df4d.html"},
               {"pk":"33", "title":"团购：北京博睿夜时尚台球俱乐部（西城区），7.9元，畅打一小时", "description":"7.9元，畅打一小时", "time":"2014.1.9 至 2014.4.8", "baidu_lat":"39.8893789", "baidu_lng":"116.3578907", "tel":"010-52885044", "address":"北京西城区枣林前街145号（白纸坊桥向北200米辅路东）易尚诺林大酒店B1层", "link":"http://bj.meituan.com/deal/8829545.html"},
               {"pk":"117", "title":"团购：北京高谷台球俱乐部（4店通用），19元，畅打两小时", "description":"19元，畅打两小时", "time":"2014.1.10 至 2014.4.9", "baidu_lat":"39.9738183", "baidu_lng":"116.4473156", "tel":"010-64220811", "address":"北京朝阳区西坝河北里7号院（国美电器院内）", "link":"http://bj.meituan.com/deal/6420513.html"},
               {"pk":"116", "title":"团购：北京高谷台球俱乐部（4店通用），19元，畅打两小时", "description":"19元，畅打两小时", "time":"2014.1.10 至 2014.4.9", "baidu_lat":"39.9598277", "baidu_lng":"116.3877299", "tel":"010-82066296", "address":"北京市西城区德胜门外教场口街9号B1楼", "link":"http://bj.meituan.com/deal/6420513.html"},
               {"pk":"115", "title":"团购：北京高谷台球俱乐部（4店通用），19元，畅打两小时", "description":"19元，畅打两小时", "time":"2014.1.10 至 2014.4.9", "baidu_lat":"39.9046925", "baidu_lng":"116.3848733", "tel":"010-63028058", "address":"北京西城区香炉营头条33号B1楼(庄胜崇光百货东侧)", "link":"http://bj.meituan.com/deal/6420513.html"},
               {"pk":"80", "title":"团购：北京高谷台球俱乐部（4店通用），19元，畅打两小时", "description":"19元，畅打两小时", "time":"2014.1.10 至 2014.4.9", "baidu_lat":"39.8981556", "baidu_lng":"116.3481725", "tel":"010-63456958", "address":"北京宣武区广安门外小马厂路1号院2号楼3层", "link":"http://bj.meituan.com/deal/6420513.html"},
               {"pk":"118", "title":"团购：北京东方球动力台球俱乐部（劲松），17.9元，畅打两小时", "description":"17.9元，畅打两小时", "time":"2013.6.14 至 2014.3.28", "baidu_lat":"39.8908983", "baidu_lng":"116.4687451", "tel":"010-58672882", "address":"北京朝阳区东三环南路58号院3号楼（劲松桥东北角富顿中心院内C座地下一层）", "link":"http://bj.meituan.com/deal/8338874.html"},
               {"pk":"119", "title":"团购：北京天瞳世家桌球会所（建外大街），36元，畅打三小时+可乐雪碧任选两瓶", "description":"36元，畅打3小时+可乐雪碧任选2瓶", "time":"2014.2.8 至 2014.8.7", "baidu_lat":"39.906204", "baidu_lng":"116.443198", "tel":"010-85677899", "address":"北京朝阳区建外大街16号东方瑞景B1层", "link":"http://bj.meituan.com/deal/6732500.html"},
               {"pk":"67", "title":"团购：北京海岸桌球俱乐部（中关村），9.9元，畅打一小时", "description":"9.9元，畅打一小时", "time":"2013.4.26 至 2014.6.30", "baidu_lat":"39.9877953", "baidu_lng":"116.3119912", "tel":"010-82569505", "address":"北京海淀区苏州街3号大河庄苑4号楼B1楼（近银科大厦）", "link":"http://bj.meituan.com/deal/9676285.html"},
               {"pk":"120", "title":"团购：北京夜时尚台球俱乐部北土城店（安贞），22元，畅打三小时", "description":"22元，畅打三小时", "time":"2014.1.11 至 2014.4.10", "baidu_lat":"39.9792718", "baidu_lng":"116.3942505", "tel":"010-56126947", "address":"北京朝阳区裕民东里甲1号", "link":"http://bj.meituan.com/deal/3700379.html"},
               {"pk":"121", "title":"团购：北京深度撞击台球俱乐部（紫竹桥），28元，畅打三小时", "description":"28元，畅打三小时", "time":"2013.4.10 至 2014.4.10", "baidu_lat":"39.9498499", "baidu_lng":"116.3101027", "tel":"010-88553318", "address":"北京海淀区紫竹院路88号紫竹花园F座B1楼", "link":"http://bj.meituan.com/deal/4901769.html"},
               {"pk":"122", "title":"团购：北京球斯卡台球俱乐部朝外旗舰店（朝阳区），18元，畅打三小时", "description":"18元，畅打三小时", "time":"2013.11.27 至 2014.6.26", "baidu_lat":"39.9305889", "baidu_lng":"116.4447598", "tel":"010-65801148", "address":"北京朝阳区朝外大街19号华普大厦B1层", "link":"http://bj.meituan.com/deal/1938412.html"},               
               {"pk":"123", "title":"团购：北京夜时尚台球对外经贸店（对外经贸），38元，畅打三小时", "description":"38元，畅打三小时", "time":"2013.11.28 至 2014.2.27", "baidu_lat":"39.9828042", "baidu_lng":"116.4333529", "tel":"010-84639810", "address":"北京朝阳区芍药居元大都对外经贸大学南门对面", "link":"http://bj.meituan.com/deal/5776951.html"},
               {"pk":"124", "title":"团购：北京8号炫酷台球俱乐部（上地），35.9元，畅打两小时", "description":"35.9元，畅打两小时", "time":"2013.10.28 至 2014.2.27", "baidu_lat":"40.0389396", "baidu_lng":"116.3255305", "tel":"010-82783058", "address":"北京海淀区上地佳园底商36号（上地城铁站对面）", "link":"http://bj.meituan.com/deal/7356822.html"},
               {"pk":"125", "title":"团购：北京悠悠台球俱乐部（回龙观），19.9元，畅打两小时", "description":"19.9元，畅打两小时", "time":"2013.4.18 至 2014.3.15", "baidu_lat":"40.0781526", "baidu_lng":"116.3248362", "tel":"010-80779687", "address":"北京昌平区回龙观龙泽苑综合楼北配楼", "link":"http://bj.meituan.com/deal/4037338.html"},
               {"pk":"126", "title":"团购：北京夜时尚台球俱乐部立水桥店（立水桥），38元，畅打两小时", "description":"38元，畅打两小时", "time":"2013.6.20 至 2014.4.8", "baidu_lat":"40.0539800", "baidu_lng":"116.4170132", "tel":"010-84671325", "address":"北京朝阳区立清路8号明天第一城7号院蓝黛时空汇B1楼（近立军路）", "link":"http://bj.meituan.com/deal/4322861.html"},
               {"pk":"127", "title":"团购：北京技艺台球俱乐部（东城区），25元，畅打三小时", "description":"25元，畅打三小时", "time":"2013.5.8 至 2014.5.5", "baidu_lat":"39.9036978", "baidu_lng":"116.4399315", "tel":"18612883001", "address":"北京东城区东花市大街35号旁", "link":"http://bj.meituan.com/deal/4828388.html"},
               {"pk":"128", "title":"团购：北京晟世台球俱乐部（和平里），8.8元，畅打一小时", "description":"8.8元，畅打一小时", "time":"2014.1.29 至 2014.4.28", "baidu_lat":"39.9636304", "baidu_lng":"116.4259469", "tel":"010-84217770", "address":"北京东城区和平里中街19号天元和平商业大厦B1楼", "link":"http://bj.meituan.com/deal/1664990.html"},
               {"pk":"129", "title":"团购：北京酷塞台球俱乐部（黄村），29.9元，畅打两小时", "description":"29.9元，畅打两小时", "time":"2014.1.8 至 2014.6.7", "baidu_lat":"39.7592469", "baidu_lng":"116.3405489", "tel":"010-69248188", "address":"北京大兴区小营路北（聚莎苑酒店院内）", "link":"http://bj.meituan.com/deal/6145824.html"},
               {"pk":"130", "title":"团购：北京万赢亿胜台球俱乐部（昌平），24元，畅打三小时", "description":"24元，畅打三小时", "time":"2013.9.7 至 2014.2.28", "baidu_lat":"40.2189029", "baidu_lng":"116.2549190", "tel":"010-80107398", "address":"北京昌平区南环东路32-5号（东关南里小区南门对面）", "link":"http://bj.meituan.com/deal/2937309.html"},
               {"pk":"131", "title":"团购：北京天陆台球俱乐部（大钟寺），16元，畅打两小时", "description":"16元，畅打两小时", "time":"2013.8.6 至 2014.8.6", "baidu_lat":"39.9682577", "baidu_lng":"116.3490755", "tel":"010-62139909", "address":"北京海淀区四道口路甲5号文林大厦B2楼", "link":"http://bj.meituan.com/deal/5481053.html"},
               {"pk":"132", "title":"团购：北京奥亨黑八台球俱乐部劲松店（劲松），8.8元，畅打八小时", "description":"8.8元，畅打八小时", "time":"2014.1.8 至 2014.4.7", "baidu_lat":"39.8885129", "baidu_lng":"116.4672264", "tel":"010-67739348", "address":"北京朝阳区劲松三区328楼地下一层（劲松地铁站D口加油站旁）", "link":"http://bj.meituan.com/deal/5381708.html"},
               {"pk":"133", "title":"团购：北京球动力总部样板店（小营），19.8元，畅打两小时", "description":"19.8元，畅打两小时", "time":"2013.9.26 至 2014.4.24", "baidu_lat":"40.0081107", "baidu_lng":"116.3795949", "tel":"010-58236022", "address":"北京朝阳区大屯路甲166号欧陆经典风格派（近欧陆经典）", "link":"http://bj.meituan.com/deal/1874810.html"},
               {"pk":"134", "title":"团购：北京卓凡台球俱乐部（建国门/北京站），17.9元，畅打三小时", "description":"17.9元，畅打三小时", "time":"2014.1.17 至 2014.7.16", "baidu_lat":"39.9050354", "baidu_lng":"116.4453862", "tel":"010-51236791", "address":"北京东城区白桥大街2号（如家酒店北门地下二层卓凡台球俱乐部）", "link":"http://bj.meituan.com/deal/9539588.html"},
               {"pk":"135", "title":"团购：北京亚星台球俱乐部（望京），14.9元，畅打两小时", "description":"14.9元，畅打两小时", "time":"2013.10.1 至 2014.2.28", "baidu_lat":"40.0078049", "baidu_lng":"116.4691712", "tel":"010-84723343", "address":"北京朝阳区南湖中园130号B1楼", "link":"http://bj.meituan.com/deal/3862360.html"},
               {"pk":"136", "title":"团购：北京夜时尚台球俱乐部万柳桥首经贸店（夏家胡同/纪家庙），29.8元，畅打三小时", "description":"29.8元，畅打三小时", "time":"2013.6.25 至 2014.3.24", "baidu_lat":"39.8542831", "baidu_lng":"116.3265186", "tel":"010-83615939", "address":"北京丰台区丰台东路育芳园19号新时特购物广场B1（距地铁10号线首经贸站约450米）", "link":"http://bj.meituan.com/deal/6041788.html"},
               {"pk":"51", "title":"团购：北京忘忧地带台球俱乐部（紫竹桥），29.9元，畅打三小时", "description":"29.9元，畅打三小时", "time":"2013.10.25 至 2014.10.24", "baidu_lat":"39.9492522", "baidu_lng":"116.3184638", "tel":"010-68726737", "address":"北京海淀区紫竹桥东北角广源大厦东侧口内B1层", "link":"http://bj.meituan.com/deal/3800478.html"},
               {"pk":"137", "title":"团购：北京98台球俱乐部（回龙观），12元，畅打一小时", "description":"12元，畅打一小时", "time":"2014.1.24 至 2014.3.31", "baidu_lat":"40.0881677", "baidu_lng":"116.3647790", "tel":"010-80752885", "address":"北京昌平区回龙观和谐家园二区西门", "link":"http://bj.meituan.com/deal/5129093.html"},
               {"pk":"138", "title":"团购：北京益嘉盈点台球俱乐部（北下关），9.9元，畅打一小时", "description":"9.9元，畅打一小时", "time":"2013.8.22 至 2014.5.31", "baidu_lat":"39.9567882", "baidu_lng":"116.3613402", "tel":"010-62247477", "address":"北京海淀区西直门北大街甲43号金运大厦B座B1楼（中信银行金运大厦支行地下）", "link":"http://bj.meituan.com/deal/1356165.html"},
               {"pk":"139", "title":"团购：北京翔天畅海台球俱乐部（牡丹园/北太平庄），19.9元，畅打两小时", "description":"19.9元，畅打两小时", "time":"2013.8.1 至 2014.8.1", "baidu_lat":"39.9733928", "baidu_lng":"116.3743438", "tel":"010-62050784", "address":"北京海淀区北三环中路32号二层（北太平桥西路南，超市发西侧2楼）", "link":"http://bj.meituan.com/deal/4786373.html"},
               {"pk":"140", "title":"团购：北京后海银锭台球俱乐部（后海/什刹海），19.9元，畅打两小时", "description":"19.9元，畅打两小时", "time":"2013.10.14 至 2014.4.13", "baidu_lat":"39.9448192", "baidu_lng":"116.4015269", "tel":"010-64020227", "address":"北京西城区地安门外大街31号（后海天堂慢摇吧对面）", "link":"http://bj.meituan.com/deal/4281059.html"},
               {"pk":"141", "title":"团购：北京和平8号台球俱乐部（安贞），35元，畅打四小时", "description":"35元，畅打四小时", "time":"2013.9.12 至 2014.6.9", "baidu_lat":"39.9680593", "baidu_lng":"116.4376271", "tel":"010-52182575", "address":"北京朝阳区和平街青年沟东路8号B1楼", "link":"http://bj.meituan.com/deal/2098095.html"},
               {"pk":"142", "title":"团购：北京当代之光台球俱乐部（亚运村），18.8元，畅打两小时", "description":"18.8元，畅打两小时", "time":"2013.3.26 至 2014.7.23", "baidu_lat":"40.0053313", "baidu_lng":"116.4197569", "tel":"010-64969588", "address":"北京朝阳区慧中北路安慧北里逸园28号楼", "link":"http://bj.meituan.com/deal/9676931.html"},
               {"pk":"143", "title":"团购：北京博登台球俱乐部（万柳），19元，畅打一小时", "description":"19元，畅打一小时", "time":"2013.11.23 至 2014.11.22", "baidu_lat":"39.9665855", "baidu_lng":"116.3089033", "tel":"010-58815361", "address":"北京海淀区长春桥路11号万柳亿城中心C座B1楼（近浏阳河大酒店）", "link":"http://bj.meituan.com/deal/6777317.html"},
               {"pk":"144", "title":"团购：北京朋海园台球俱乐部（黄村），22元，畅打两小时", "description":"22元，畅打两小时", "time":"2014.1.15 至 2014.4.14", "baidu_lat":"39.7371972", "baidu_lng":"116.3416940", "tel":"010-69294327", "address":"北京大兴区西大街大兴医院9号楼地下一层", "link":"http://bj.meituan.com/deal/5386176.html"},
               {"pk":"145", "title":"团购：北京520台球俱乐部（劲松），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2014.1.18 至 2015.1.17", "baidu_lat":"39.8858748", "baidu_lng":"116.4741308", "tel":"010-87379688", "address":"北京朝阳区武圣东里农光里市场斜对面206号楼（木屋烧烤楼下）地下一层", "link":"http://bj.meituan.com/deal/9895972.html"},
               {"pk":"146", "title":"团购：北京星期8台球俱乐部（回龙观），12元，畅打一小时", "description":"12元，畅打一小时", "time":"2013.11.26 至 2014.2.25", "baidu_lat":"40.0968995", "baidu_lng":"116.3120102", "tel":"010-61779510", "address":"北京昌平区回龙观北农酒店西侧华北电力大学北门", "link":"http://bj.meituan.com/deal/6654307.html"},
               {"pk":"148", "title":"团购：北京黑桃8撞球馆上坡家园店（3店通用），18元，畅打一小时", "description":"18元，畅打一小时", "time":"2013.10.31 至 2014.10.28", "baidu_lat":"40.0899531", "baidu_lng":"116.3702907", "tel":"18911796160", "address":"北京昌平区济远街与龙锦3街交叉路口东行20米路南B1层", "link":"http://bj.meituan.com/deal/8637559.html"},
               {"pk":"147", "title":"团购：北京黑桃8撞球馆旺龙花园店（3店通用），18元，畅打一小时", "description":"18元，畅打一小时", "time":"2013.10.31 至 2014.10.28", "baidu_lat":"40.0869599", "baidu_lng":"116.3729226", "tel":"18911706160", "address":"北京昌平区东小口镇霍营旺龙花园底商11号", "link":"http://bj.meituan.com/deal/8637559.html"},
               {"pk":"149", "title":"团购：北京黑桃8撞球馆紫金新干线小区店（3店通用），18元，畅打一小时", "description":"18元，畅打一小时", "time":"2013.10.31 至 2014.10.28", "baidu_lat":"40.0856005", "baidu_lng":"116.3859510", "tel":"18911706160", "address":"北京昌平区紫金新干线小区底商", "link":"http://bj.meituan.com/deal/8637559.html"},
               {"pk":"150", "title":"团购：北京璟点台球俱乐部昌平鼓楼西街店（昌平镇），22元，畅打三小时", "description":"22元，畅打三小时", "time":"2013.10.24 至 2014.10.23", "baidu_lat":"40.2297910", "baidu_lng":"116.2369225", "tel":"010-80101023", "address":"北京昌平区鼓楼西街12号地下（工商银行对面）", "link":"http://bj.meituan.com/deal/5739483.html"},
               {"pk":"151", "title":"团购：北京金福德台球俱乐部（双井），20元，畅打两小时", "description":"20元，畅打两小时", "time":"2014年01月08日至2014年07月31日", "baidu_lat":"39.8999641", "baidu_lng":"116.4526116", "tel":"010-67735898", "address":"北京朝阳区忠实里南街甲6乙6号楼负一层", "link":"http://bj.nuomi.com/deal/5ecuu4m4.html"},
               {"pk":"152", "title":"团购：北京夜时尚台球俱乐部通州北苑店（通州北苑），9.9元，畅打两小时", "description":"9.9元，畅打两小时", "time":"2013年11月12日至2014年03月16日", "baidu_lat":"39.9048952", "baidu_lng":"116.6457678", "tel":"010-52898803", "address":"北京通州区北苑南路鑫苑小区B1层", "link":"http://bj.nuomi.com/deal/iww3xjpc.html"},
               {"pk":"153", "title":"团购：北京速D台球俱乐部（传媒大学），19.8元，畅打两小时", "description":"19.8元，畅打两小时", "time":"2013年12月25日至2014年03月31日", "baidu_lat":"39.9293697", "baidu_lng":"116.5566050", "tel":"010-65775398", "address":"北京朝阳区朝阳北路白家楼桥东58号楼B1层", "link":"http://bj.nuomi.com/deal/yxxjbcvo.html"},
               {"pk":"154", "title":"团购：北京星期5台球俱乐部（洋桥），22元，畅打两小时", "description":"22元，畅打两小时", "time":"2014年01月29日至2014年06月30日", "baidu_lat":"39.8561241", "baidu_lng":"116.3947374", "tel":"010-51215593", "address":"北京丰台区马家堡东口洋桥大厦B1层", "link":"http://bj.nuomi.com/deal/et5kwleo.html"},
               {"pk":"155", "title":"团购：北京金色年华台球俱乐部（劲松），18元，畅打两小时", "description":"18元，畅打两小时", "time":"2013年06月09日-2014年06月08日", "baidu_lat":"39.8951752", "baidu_lng":"116.4659855", "tel":"010-67751145", "address":"北京朝阳区劲松垂杨柳东里38号", "link":"http://bj.nuomi.com/deal/by8s1uy4.html"},
               {"pk":"27", "title":"团购：北京凯乐台球俱乐部（苹果园），29.9元，畅打三小时", "description":"29.9元，畅打三小时", "time":"2013年09月03日-2014年04月01日", "baidu_lat":"39.9350493", "baidu_lng":"116.2191068", "tel":"010-88705828 ", "address":"石景山西黄新村雍景四季东门（北方工业大学北门） ", "link":"http://bj.nuomi.com/deal/krhcnvzo.html"},
               {"pk":"79", "title":"团购：北京球动力大郊亭店（北京欢乐谷），38.8元，畅打三小时", "description":"38.8元，畅打三小时", "time":"2013年12月14日至2014年03月02日", "baidu_lat":"39.8986729", "baidu_lng":"116.5003570", "tel":"010－85788252", "address":"北京市朝阳区东四环大郊亭桥东200米（7天连锁酒店一层）", "link":"http://bj.nuomi.com/deal/hvkwctio.html"},
               {"pk":"46", "title":"团购：北京黑湖台球俱乐部顺义站前街店（顺义），18元，畅打一小时", "description":"18元，畅打一小时", "time":"2013年11月21日至2014年02月28日", "baidu_lat":"40.1311662", "baidu_lng":"116.6553110", "tel":"010-69425177", "address":"北京市顺义区站前街2号", "link":"http://bj.nuomi.com/deal/rrcoauih.html"},
               {"pk":"156", "title":"团购：北京龙辉台球俱乐部（黄村），21.8元，畅打两小时", "description":"21.8元，畅打两小时", "time":"2014年01月10日至2014年06月16日", "baidu_lat":"39.7635692", "baidu_lng":"116.3433008", "tel":"13611332193", "address":"北京大兴区康庄路28号，水晶广场写字楼6层", "link":"http://bj.nuomi.com/deal/br8kd0kn.html"},
               {"pk":"157", "title":"团购：北京蓝旗星台球俱乐部（北京大学），68元，畅打九小时", "description":"68元，畅打九小时", "time":"2013年12月30日至2014年05月02日", "baidu_lat":"39.9985814", "baidu_lng":"116.3294837", "tel":"010-62769808", "address":"北京海淀区成府路125号蓝旗营5号楼", "link":"http://bj.nuomi.com/deal/eyiqgptj.html"},
               {"pk":"158", "title":"团购：北京天成台球俱乐部（回龙观），19元，畅打两小时", "description":"19元，畅打两小时", "time":"2014年01月27日至2014年04月25日", "baidu_lat":"40.0932582", "baidu_lng":"116.3726076", "tel":"010-57240538", "address":"北京昌平区回龙观龙锦苑东一区99连锁旅馆地下一层", "link":"http://bj.nuomi.com/deal/jshsj6f0.html"},
               {"pk":"159", "title":"团购：北京金盛世纪台球俱乐部（房山），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2014年01月16日至2014年04月21日", "baidu_lat":"39.7744745", "baidu_lng":"116.1728625", "tel":"010-80327799", "address":"北京房山区加州水郡商业广场D座地下1层", "link":"http://bj.nuomi.com/deal/gclacp3t.html"},
               {"pk":"160", "title":"团购：北京撞8台球俱乐部（顺义），15元，畅打一小时", "description":"15元，畅打一小时", "time":"2013年12月23日至2014年05月07日", "baidu_lat":"40.1278487", "baidu_lng":"116.6526506", "tel":"13716685868", "address":"北京顺义区怡馨家园29号楼", "link":"http://bj.nuomi.com/deal/ztpeahfa.html"},
               {"pk":"161", "title":"团购：北京七度台球俱乐部（昌平镇），12元，畅打一小时", "description":"12元，畅打一小时", "time":"2014年01月20日至2014年04月23日", "baidu_lat":"40.2274343", "baidu_lng":"116.2630334", "tel":"13901295581", "address":"北京昌平区府学路7号福地家园", "link":"http://bj.nuomi.com/deal/tczpxqkc.html"},
               {"pk":"162", "title":"团购：北京628台球俱乐部（什刹海），28元，畅打两小时", "description":"28元，畅打两小时", "time":"2013年12月27日至2014年03月27日", "baidu_lat":"39.9392861", "baidu_lng":"116.3876966", "tel":"010-83288628", "address":"北京西城区地安门西大街143号 北大医院正对面", "link":"http://bj.nuomi.com/deal/5aicdi2s.html"},
               {"pk":"163", "title":"团购：北京国兰棋牌台球俱乐部（广渠门），18元，畅打一小时", "description":"18元，畅打一小时", "time":"2013年08月19日至2014年02月22日", "baidu_lat":"39.9027377", "baidu_lng":"116.4376252", "tel":"010-67158216", "address":"北京东城区东花市大街南小市口6号", "link":"http://bj.nuomi.com/deal/bs4r1yff.html"},
               {"pk":"164", "title":"团购：北京西上园台球俱乐部（新华大街），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2014年01月17日至2014年04月18日", "baidu_lat":"39.9097275", "baidu_lng":"116.6832917", "tel":"010-80570304", "address":"北京通州区西上园小区西门", "link":"http://bj.nuomi.com/deal/ob5gwwxk.html"},
               {"pk":"165", "title":"团购：北京雅君台球俱乐部朝外店（朝外大街），36元，畅打两小时", "description":"36元，畅打两小时", "time":"2013年11月10日至2014年03月08日", "baidu_lat":"39.9284716", "baidu_lng":"116.4486272", "tel":"010-58790918", "address":"北京朝阳区朝外大街乙12号", "link":"http://bj.nuomi.com/deal/ugz52rgn.html"},
               {"pk":"166", "title":"团购：北京君辉台球俱乐部（管庄），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年11月19日至2014年02月17日 ", "baidu_lat":"39.9177441", "baidu_lng":"116.6017418", "tel":"010-53665198", "address":"北京朝阳区杨闸环岛西plus365比格披萨地下一层", "link":"http://bj.nuomi.com/deal/ffdznqoj.html"},
               {"pk":"167", "title":"团购：北京梦幻台球俱乐部（管庄），45元，畅打两小时", "description":"45元，畅打两小时", "time":"2013年12月23日至2014年05月31日", "baidu_lat":"39.9200769", "baidu_lng":"116.5871127", "tel":"13910813970", "address":"北京朝阳区管庄西里11号楼", "link":"http://bj.nuomi.com/deal/qiytfbwk.html"},
               {"pk":"168", "title":"团购：北京K8台球俱乐部（沙河），10元，畅打一小时", "description":"10元，畅打一小时", "time":"2013年11月30日至2014年05月30日", "baidu_lat":"40.1570599", "baidu_lng":"116.2692001", "tel":"13521844695", "address":"北京昌平区沙河地铁站亿旺商场旁", "link":"http://bj.nuomi.com/deal/dewlhx1n.html"},
               {"pk":"169", "title":"团购：北京奥辉启航台球俱乐部（传媒大学），19元，畅打两小时", "description":"19元，畅打两小时", "time":"2013年10月08日至2014年03月02日", "baidu_lat":"39.9220917", "baidu_lng":"116.5529168", "tel":"13810687710", "address":"北京朝阳区朝阳路传媒大学北门对面", "link":"http://bj.nuomi.com/deal/39cki6qe.html"},
               {"pk":"170", "title":"团购：北京东绅台球俱乐部（酒仙桥），38元，畅打三小时", "description":"38元，畅打三小时", "time":"2013年10月20日-2014年02月22日", "baidu_lat":"39.9687972", "baidu_lng":"116.4970572", "tel":"010-64310217", "address":"北京朝阳区酒仙桥十一街区1楼", "link":"http://bj.nuomi.com/deal/dyvthllh.html"},
               {"pk":"107", "title":"团购：北京云川台球俱乐部志新桥店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9903301", "baidu_lng":"116.3757489", "tel":"010-62018887 ", "address":"北京海淀区北四环志新桥向南200米路西 ", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"171", "title":"团购：北京云川台球俱乐部方庄店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.8721039", "baidu_lng":"116.4421229", "tel":"010-67622828", "address":"北京市丰台区蒲方路1号", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"113", "title":"团购：北京云川台球俱乐部三里屯店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9335159", "baidu_lng":"116.4625773", "tel":"010-68085558", "address":"北京市朝阳区三里屯南路16号泰悦豪庭B1楼", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"105", "title":"团购：北京云川台球俱乐部永定门店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.8709788", "baidu_lng":"116.4130107", "tel":"010-87893336 ", "address":"北京永定门外安乐林路天天家园小区内东侧 ", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"109", "title":"团购：北京云川台球俱乐部右安门店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.8658325", "baidu_lng":"116.3708853", "tel":"010-83527770 ", "address":"北京丰台区右安门外大街99号", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"172", "title":"团购：北京云川台球俱乐部西四店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9406734", "baidu_lng":"116.3858051", "tel":"010-66166490", "address":"北京市西城区西四北大街乙158号地下一层", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"173", "title":"团购：北京云川台球俱乐部保福寺店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9861512", "baidu_lng":"116.3339893", "tel":"010-62566598", "address":"北京市海淀区中关村南三街文化体育中心2层", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"174", "title":"团购：北京云川台球俱乐部马甸店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9881982", "baidu_lng":"116.3871993", "tel":"010-62379990", "address":"北京市朝阳区华严北里甲一号", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"175", "title":"团购：北京云川台球俱乐部五道口店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9991614", "baidu_lng":"116.3465476", "tel":"010-82386906", "address":"北京市海淀区成府路23号五道口宾馆", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"176", "title":"团购：北京云川台球俱乐部定慧桥店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9352214", "baidu_lng":"116.2687430", "tel":"010-58970485", "address":"北京市海淀区永定路乙1号院14楼2门地下1层（乐府江南小区门口）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"177", "title":"团购：北京云川台球俱乐部五棵松店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9068005", "baidu_lng":"116.2879723", "tel":"010-52126635", "address":"北京市海淀区今日家园8号地下一层", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"178", "title":"团购：北京云川台球俱乐部朝阳路店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9230932", "baidu_lng":"116.5330900", "tel":"010-65104646", "address":"北京市朝阳区朝阳路世纪天乐潮青汇商场5层", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"179", "title":"团购：北京云川台球俱乐部六里桥店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.8880627", "baidu_lng":"116.3228218", "tel":"010-63333884", "address":"北京市丰台区太平桥西路华源1街4号楼（青年餐厅地下1层）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"180", "title":"团购：北京云川台球俱乐部酒仙桥店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9810040", "baidu_lng":"116.4969695", "tel":"010-64369489", "address":"北京市朝阳区酒仙桥路甲12号电子城科技大厦地下2层（临近比格餐厅）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"181", "title":"团购：北京云川台球俱乐部远洋山水店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9095537", "baidu_lng":"116.2467660", "tel":"010-88697183", "address":"北京市石景山区鲁谷东大街（远洋山水小区西门）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"182", "title":"团购：北京云川台球俱乐部岳各庄店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.8669009", "baidu_lng":"116.2657588", "tel":"010-63871652", "address":"北京市丰台区五里店卢沟桥路和光里小区2号楼地下1层（临近岳各庄检测场）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"183", "title":"团购：北京云川台球俱乐部将台路店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9721626", "baidu_lng":"116.5093368", "tel":"010-84598422", "address":"北京市朝阳区酒仙桥驼房营西里甲5号2楼云顶时尚台球俱乐部（临近乐食尚餐厅）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"184", "title":"团购：北京云川台球俱乐部良乡店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.7415050", "baidu_lng":"116.1481470", "tel":"010-69365789", "address":"北京市房山区良乡拱辰大街49号（科豪大厦4层）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"185", "title":"团购：北京云川台球俱乐部学知桥店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9796657", "baidu_lng":"116.3547898", "tel":"010-82050295", "address":"北京市海淀区知春路太月园3号楼地下一层", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"186", "title":"团购：北京云川台球俱乐部草桥店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.8515247", "baidu_lng":"116.3702949", "tel":"010-51471999", "address":"北京市丰台区北甲地路10号院三层", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"187", "title":"团购：北京云川台球俱乐部大屯店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"", "baidu_lng":"40.0093974", "tel":"116.4153867", "address":"北京市朝阳区亚运村安立路66号安立花园1号楼", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"188", "title":"团购：北京云川台球俱乐部新街口店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9444717", "baidu_lng":"116.3737303", "tel":"010-66537177", "address":"北京市西城区西直门内赵登禹路冠英园西区20楼B1楼(近地铁4号线新街口站D口)", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"189", "title":"团购：北京云川台球俱乐部交大店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9557359", "baidu_lng":"116.3543208", "tel":"010-82164788", "address":"北京市海淀区交大东路25号", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"190", "title":"团购：北京云川台球俱乐部白纸坊店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.8828696", "baidu_lng":"116.3533838", "tel":"010-63388918", "address":"北京市丰台区鸭子桥路信德园小区5-7（临近农业银行）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"191", "title":"团购：北京云川台球俱乐部花园桥店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9381604", "baidu_lng":"116.2958428", "tel":"010-88138880", "address":"北京市海淀区八里庄北里23号楼2层（临近碧水云天洗浴中心）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"192", "title":"团购：北京云川台球俱乐部丰体店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.8580647", "baidu_lng":"116.2928752", "tel":"010-63865550", "address":"北京市丰台区文体路58号（丰体工人俱乐部地下2层）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"193", "title":"团购：北京云川台球俱乐部鲁谷店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9078076", "baidu_lng":"116.2467837", "tel":"010-88697770", "address":"北京市石景山区雕塑园南街29号楼远洋山水小区东门（远洋山水售楼处地下1层）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"194", "title":"团购：北京云川台球俱乐部成寿寺店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.8596740", "baidu_lng":"116.4446929", "tel":"010-51228316", "address":"北京市丰台区方庄南路9号院方庄桥南300米（谱田大厦B1层）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"195", "title":"团购：北京云川台球俱乐部石佛营店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9351938", "baidu_lng":"116.5114810", "tel":"010-85819589", "address":"北京市朝阳区石佛营炫特区西门商业楼3层（临近卜蜂莲花超市）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"196", "title":"团购：北京云川台球俱乐部正阳桥店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.8559464", "baidu_lng":"116.2941854", "tel":"010-63833680转0", "address":"北京市丰台区正阳大街正阳北里18号楼底商1层（临近北京国阳医院）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"197", "title":"团购：北京云川台球俱乐部四惠店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9176263", "baidu_lng":"116.5012654", "tel":"010-85865147", "address":"北京市朝阳区八里庄西里75号楼远洋天地小区南门（临近四惠地铁站D口）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"198", "title":"团购：北京云川台球俱乐部广外店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.8923402", "baidu_lng":"116.3462058", "tel":"010-63334440", "address":"北京市西城区宣武门广安门外红居街5号楼", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"199", "title":"团购：北京云川台球俱乐部丰台东路店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.8543703", "baidu_lng":"116.3225823", "tel":"010-83619585", "address":"北京市丰台区丰台东路樊家村甲3号", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"200", "title":"团购：北京云川台球俱乐部马家堡店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.8437473", "baidu_lng":"116.3711004", "tel":"010-67570773", "address":"北京市丰台区马家堡嘉园路星河苑小区西门（安太妇产医院对面）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"201", "title":"团购：北京云川台球俱乐部九州店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9568581", "baidu_lng":"116.2797742", "tel":"010-88498575", "address":"北京市海淀区西四环北路71号郦城A区3号楼地下一层", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"202", "title":"团购：北京云川台球俱乐部望京店（36店通用），30元，畅打两小时", "description":"30元，畅打两小时", "time":"2013年12月07日至2014年03月31日", "baidu_lat":"39.9925667", "baidu_lng":"116.4852965", "tel":"010-64773066", "address":"北京市朝阳区广顺大街19号院会所（临近新世界百货）", "link":"http://bj.nuomi.com/deal/cpiv9rzm.html"},
               {"pk":"203", "title":"团购：北京奕承龙台球俱乐部，28元，畅打两小时", "description":"28元，畅打两小时", "time":"2014-01-01至2014-04-01", "baidu_lat":"39.8570611", "baidu_lng":"116.3160968", "tel":"010-84001818", "address":"北京丰台区丰桥路8号院甲1号楼1-09号三环新城底商", "link":"http://t.dianping.com/deal/2102963"},
               {"pk":"", "title":"团购：北京", "description":"", "time":"", "baidu_lat":"", "baidu_lng":"", "tel":"", "address":"", "link":""}
               ]
    return coupons

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
    helpmessage = "您好，需要帮助吗？\r\n1、发送您的位置信息，获取附近台球俱乐部信息。\r\n2、输入“中式八球”，“花式台球”获取我们精选的台球视频集锦。\r\n3、发送相片，图片，一起和身边的朋友们交换互动。\r\n4、输入“找便宜”，“团购”获取超值台球团购。\r\n5、输入“比赛”，“活动”获取俱乐部比赛活动信息。\r\n祝各位球友们玩得开心，愉快，谢谢关注。"
    content = {
      #English content
      "hi":"Hello",
      "fj":"您想找附近的台球俱乐部吗？请发送您的位置给我们，给您推荐身边的台球俱乐部。",
      "bs":"您想找台球俱乐部举办的比赛吗？",
      "nh":"你好啊，朋友",
      "bz":"您好，需要帮助吗？\r\n1、发送您的位置信息，获取附近台球俱乐部信息。\r\n2、输入“中式八球”，“花式台球”获取我们精选的台球视频集锦。\r\n3、发送相片，图片，一起和身边的朋友们交换互动。\r\n4、输入“找便宜”，“团购”获取超值台球团购。\r\n5、输入“比赛”，“活动”获取俱乐部比赛活动信息。\r\n祝各位球友们玩得开心，愉快，谢谢关注。",
      "zf":"送祝福啦，祝您马年吉祥，身体健康，马到成功，财源滚滚来！",
      "help":"您好，需要帮助吗？\r\n1、发送您的位置信息，获取附近台球俱乐部信息。\r\n2、输入“中式八球”，“花式台球”获取我们精选的台球视频集锦。\r\n3、发送相片，图片，一起和身边的朋友们交换互动。\r\n4、输入“找便宜”，“团购”获取超值台球团购。\r\n5、输入“比赛”，“活动”获取俱乐部比赛活动信息。\r\n祝各位球友们玩得开心，愉快，谢谢关注。",
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
      u"帮助":"您好，需要帮助吗？\r\n1、发送您的位置信息，获取附近台球俱乐部信息。\r\n2、输入“中式八球”，“花式台球”获取我们精选的台球视频集锦。\r\n3、发送相片，图片，一起和身边的朋友们交换互动。\r\n4、输入“找便宜”，“团购”获取超值台球团购。\r\n5、输入“比赛”，“活动”获取俱乐部比赛活动信息。\r\n祝各位球友们玩得开心，愉快，谢谢关注。",
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
      "?":"您好，需要帮助吗？\r\n1、发送您的位置信息，获取附近台球俱乐部信息。\r\n2、输入“中式八球”，“花式台球”获取我们精选的台球视频集锦。\r\n3、发送相片，图片，一起和身边的朋友们交换互动。\r\n4、输入“找便宜”，“团购”获取超值台球团购。\r\n5、输入“比赛”，“活动”获取俱乐部比赛活动信息。\r\n祝各位球友们玩得开心，愉快，谢谢关注。",
      u"？":"您好，需要帮助吗？\r\n1、发送您的位置信息，获取附近台球俱乐部信息。\r\n2、输入“中式八球”，“花式台球”获取我们精选的台球视频集锦。\r\n3、发送相片，图片，一起和身边的朋友们交换互动。\r\n4、输入“找便宜”，“团购”获取超值台球团购。\r\n5、输入“比赛”，“活动”获取俱乐部比赛活动信息。\r\n祝各位球友们玩得开心，愉快，谢谢关注。"
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
          coupons = set_coupon(request)
          for i in range(len(coupons)):
              if coupons[i]['pk'] == pkid:
                  coupontitle = coupons[i]['title']
                  coupondescription = coupons[i]['description']
                  couponlink = coupons[i]['link']
                  echopictext = pictext2Tpl % (
                                   msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                                   title, discription, picurl, originContent,coupontitle, coupondescription,picurl,couponlink) 
                  return echopictext
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
        elif msg['Content'] == "团购" or msg['Content'] == "找便宜" or msg['Content'] == "优惠":
          coupons = set_coupon(request)
          couponsid = randint(0,len(coupons)-1)
          lat_baidu = coupons[couponsid]['baidu_lat']
          lng_baidu = coupons[couponsid]['baidu_lng']
          pkid = coupons[couponsid]['pk']
          picurl = "http://api.map.baidu.com/staticimage?center="+lng_baidu+","+lat_baidu+"&width=450&height=300&zoom=18&scale=2&markers="+lng_baidu+","+lat_baidu+"&markerStyles=-1,"+"http://billiardsalbum.bcs.duapp.com/2014/01/marker-2.png"
          weblink = "http://www.pktaiqiu.com/poolroom/"+pkid
          echopictext = pictext2Tpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           coupons[couponsid]['title'], "地址："+coupons[couponsid]['address']+"\r\n电话："+coupons[couponsid]['tel']+"\r\n\r\n查看详情，请点击阅读全文", picurl, coupons[couponsid]['link'],"俱乐部详情", "description",picurl,weblink)          
          return echopictext
        elif msg['Content'] == "云川" or msg['Content'] == "yunchuan" or msg['Content'] == "yc":
          coupons = set_yunchuan_coupon(request)
          couponsid = randint(0,len(coupons)-1)
          lat_baidu = coupons[couponsid]['baidu_lat']
          lng_baidu = coupons[couponsid]['baidu_lng']
          pkid = coupons[couponsid]['pk']
          picurl = "http://api.map.baidu.com/staticimage?center="+lng_baidu+","+lat_baidu+"&width=450&height=300&zoom=18&scale=2&markers="+lng_baidu+","+lat_baidu+"&markerStyles=-1,"+"http://billiardsalbum.bcs.duapp.com/2014/01/marker-2.png"
          weblink = "http://www.pktaiqiu.com/poolroom/"+pkid
          echopictext = pictext2Tpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           coupons[couponsid]['title'], "地址："+coupons[couponsid]['address']+"\r\n电话："+coupons[couponsid]['tel']+"\r\n\r\n查看详情，请点击阅读全文", picurl, coupons[couponsid]['link'],"俱乐部详情", "description",picurl,weblink)          
          return echopictext
        elif msg['Content'] == "活动":
          acts = set_act(request)
          echopictext = pictext2Tpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           acts[0]['title'], acts[0]['detail'], acts[0]['picurl'], acts[0]['link'],acts[1]['title'], acts[1]['detail'], acts[1]['picurl'], acts[1]['link'])          
          return echopictext
        elif msg['Content'] == "比赛":
          matches = set_match(request)
          echopictext = pictextTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           matches[0]['title'], '', 'http://billiardsalbum.bcs.duapp.com/2014/01/404.jpg', 'http://www.pktaiqiu.com/match/75/')          
          return echopictext
        else:
          replywords = msg['Content']
          helpmessage = "您好，需要帮助吗？\r\n1、发送您的位置信息，获取附近台球俱乐部信息。\r\n2、输入“中式八球”，“花式台球”获取我们精选的台球视频集锦。\r\n3、发送相片，图片，一起和身边的朋友们交换互动。\r\n4、输入“找便宜”，“团购”获取超值台球团购。\r\n5、输入“比赛”，“活动”获取俱乐部比赛活动信息。\r\n祝各位球友们玩得开心，愉快，谢谢关注。"
          echostr = textTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           helpmessage)
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









