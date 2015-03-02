# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2013年10月21日

@author: kane
'''

from django.db import models
from django.utils.timezone import localtime, pytz, utc
from bitfield import BitField
from django.utils.encoding import force_unicode
from django.contrib.auth.models import User
from billiards.storage import ImageStorage
from billiards.settings import UPLOAD_TO, TIME_ZONE, MEDIA_URL, BAE_IMAGE,\
    THUMBNAIL_WIDTH, ESCORT_HEIGHT
import datetime
import os
from django.db.models.query_utils import Q
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
import sys
from django.db.models.fields import CharField
from billiards import settings
from billiards.id import generator
from billiards.citydistrict import CITY_DISTRICT
import string
from uuidfield.fields import UUIDField
from decimal import Decimal
from geosimple.fields import GeohashField
from geosimple.managers import GeoManager
from billiards.commons import decodeunicode, notification_msg
import time
from django.utils import simplejson
import logging

logger = logging.getLogger("billiards")

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

def getThumbnailPath(path, length, prefix = 'w'):
    fileName, fileExtension = os.path.splitext(path)
    return "%s-%s%s%s" %(fileName, prefix, length, fileExtension)

def toDict(bitfield):
    flag_dict = {}
    for f in bitfield:
        flag_dict[f[0]] = f[1]
    return flag_dict

def bitLabelToList(bitfield):
    return [bitfield.get_label(f[0]) for f in bitfield if f[1]]

def bitToList(bitfield):
    return [f[0] for f in bitfield if f[1]]

poolroom_fields = ('uuid', 'name', 'address', 'tel', 'lat_baidu', 'lng_baidu', 'flags', 'businesshours', 'size', 'rating')

def getCouponCriteria(theday = None):
    datefmt = "%Y-%m-%d"
    if theday == None:
        theday = datetime.datetime.today()
    return Q(startdate__lte=theday.strftime(datefmt)) & \
        (Q(enddate__isnull=True) | Q(enddate__gte=theday.strftime(datefmt))) & \
        Q(status=1)
        
class Poolroom(models.Model):
    uuid = UUIDField(auto=True, hyphenate=True, unique=True)
    name = models.CharField(max_length=200,null=False,verbose_name='名字')
    address = models.TextField(null=True,verbose_name='地址')
    tel = models.CharField(max_length=20,null=True,verbose_name='电话')
    lat = models.DecimalField(max_digits=11,decimal_places=7,null=True,verbose_name='纬度_google地图')
    lng = models.DecimalField(max_digits=11,decimal_places=7,null=True,verbose_name='经度_google地图')
    lat_baidu = models.DecimalField(max_digits=11,decimal_places=7,null=True,verbose_name='纬度_百度地图')
    lng_baidu = models.DecimalField(max_digits=11,decimal_places=7,null=True,verbose_name='经度_百度地图')
    #TODO try composite bit field
    flags = BitField(flags=(
            ('wifi', u'Wifi'),
            ('wifi_free', u'免费Wifi'),
            ('parking', u'停车位'),
            ('parking_free', u'免费停车位'),
            ('cafeteria', u'餐厅'),
            ('subway', u'地铁周边'),
            ('nosmoking', u'禁烟'),
            ('nosmokingarea', u'无烟区'),
            ('redbullpartner', u'红牛合作球房'),
        ), verbose_name='特色属性')
    businesshours = models.CharField(max_length=60,null=True,verbose_name='营业时间')
    size = models.IntegerField(max_length=8,null=True,verbose_name='球馆面积(平米)')
    rating = models.IntegerField(max_length=2,null=True,verbose_name='球房总评分')
    review = models.CharField(max_length=1024,null=True,blank=True,verbose_name='球房介绍')
    city = models.IntegerField(verbose_name=u'城市', choices=CITY_DISTRICT.values(), default=10,)
    district = models.CharField(verbose_name=u'行政区', max_length=10)
    exist = models.IntegerField(verbose_name=u'是否还存在', choices=(
            (1, u'正常'),
            (2, u'已倒闭'),
            (3, u'暂时停业'),
        ), default=1)
    location = GeohashField()

    class Meta:
        db_table = 'poolroom'
        verbose_name = '台球厅'
        verbose_name_plural = '台球厅'

    def __unicode__(self):
        return self.name

    def natural_key(self):
        images = {}
        for idx, image in enumerate(self.images):
            newimage = {}
            newimage['imagepath'] = image.imagepath.name
            newimage['iscover'] = image.iscover
            newimage['description'] = image.description
            images['img' + str(idx)] = newimage
        return {'uuid': str(self.uuid), 'name': self.name, 'lat': float(self.lat_baidu), 'lng': float(self.lng_baidu),
                'businesshours': self.businesshours, 'size': self.size,
                'address': self.address, 'flags': toDict(self.flags), 'rating': self.rating,
                'images': images}

    def natural_key_simple(self):
        return {'uuid': str(self.uuid), 'name': self.name, 'lat': float(self.lat_baidu), 'lng': float(self.lng_baidu)}
        
    objects = GeoManager()
        
    @property
    def uuidstr(self):
        return str(self.uuid)
    
    @property
    def images(self):
        return PoolroomImage.objects.filter(Q(poolroom=self) & Q(status=1))
    
    @property
    def coupons(self):
        return self.getCoupons(datetime.datetime.today())
    
    def getCoupons(self, date):
        return Coupon.objects.filter(Q(poolroom=self) & getCouponCriteria(date))
    
UPLOAD_TO_POOLROOM = UPLOAD_TO + 'poolroom/'
poolroomimage_fields = ('imagepath', 'description', 'iscover')
poolroomcoupon_fields = ('title', 'description', 'discount', 'url')
class PoolroomImage(models.Model):
    id = models.AutoField(primary_key=True)
    poolroom = models.ForeignKey(Poolroom, verbose_name='台球厅')
    imagepath = models.ImageField(verbose_name=u'选择本地图片/图片路径', max_length=250, upload_to=UPLOAD_TO_POOLROOM, 
                                  storage=ImageStorage())
    description = models.CharField(verbose_name=u'图片说明', null=True, blank=True, max_length=50)
    iscover = models.BooleanField(verbose_name=u'是否是封面图片', default=False)
    status = models.IntegerField(verbose_name=u'状态', choices=(
            (0, u'不可用'),
            (1, u'可用'),
        ), default=1,)
    
    class Meta:
        db_table = 'poolroom_images'
        verbose_name = '台球厅图片'
        verbose_name_plural = '台球厅图片'
        
    def imagetag(self):
        return u'<img src="%s%s" />' %(MEDIA_URL, self.imagepath)
    imagetag.short_description = u'图片预览'
    imagetag.allow_tags = True

    def __unicode__(self):
        return self.poolroom.name + "-" + self.description
    
    __imagepath = None
    
    def __init__(self, *args, **kwargs):
        super(PoolroomImage, self).__init__(*args, **kwargs)
        self.__imagepath = self.imagepath
    
    def save(self):
        super(PoolroomImage, self).save()
        
        if self.imagepath != self.__imagepath:
            # avoid import issue in local env
            # https://github.com/BaiduAppEngine/bae-python-sdk/issues/1
            try:
                from bae_image.image import BaeImage
                img = BaeImage(BAE_IMAGE['key'], BAE_IMAGE['secret'], BAE_IMAGE['host'])
                albumstorage = ImageStorage()
                path = str(self.imagepath)
                import base64
                for width in THUMBNAIL_WIDTH:
                    img.clearOperations()
                    img.setSource(MEDIA_URL + path)
                    img.setZooming(BaeImage.ZOOMING_TYPE_WIDTH, width)
                    ret = img.process()
                    body = ret['response_params']['image_data']
                
                    newpath = getThumbnailPath(path, width)
                    albumstorage.saveToBucket(newpath, base64.b64decode(body))
            except ImportError:
                pass
        self.__imagepath = self.imagepath

@receiver(pre_delete, sender=PoolroomImage)
def delete_image(instance, **kwargs):
    try:
        instance.imagepath.storage.delete(instance.imagepath.name)
    except Exception:
        pass
    for width in THUMBNAIL_WIDTH:
        try:
            instance.imagepath.storage.delete(PoolroomImage.getThumbnailPath(instance.imagepath.name, width))
        except Exception:
            pass
            
class ChoiceTypeField(models.CharField):
    ''' use value of key when serializing as json
    '''
    jsonUseValue = True
    exportUseValue = True
    def __init__(self, *args, **kwargs):
        if 'jsonUseValue' in kwargs:
            self.jsonUseValue = kwargs['jsonUseValue']
            del kwargs['jsonUseValue']
        if 'exportUseValue' in kwargs:
            self.exportUseValue = kwargs['exportUseValue']
            del kwargs['exportUseValue']
        super(ChoiceTypeField, self).__init__(*args, **kwargs)
        
    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        if sys._getframe(2).f_code.co_name == 'serialize':
            return value
        return force_unicode(dict(self.flatchoices).get(value, value), strings_only=True)
    
    def json_use_value(self):
        return self.jsonUseValue
    
    def export_use_value(self):
        return self.exportUseValue
    
class IntegerChoiceTypeField(models.IntegerField):
    ''' use value of key when serializing as json
    '''
    jsonUseValue = True
    exportUseValue = True
    def __init__(self, *args, **kwargs):
        if 'jsonUseValue' in kwargs:
            self.jsonUseValue = kwargs['jsonUseValue']
            del kwargs['jsonUseValue']
        if 'exportUseValue' in kwargs:
            self.exportUseValue = kwargs['exportUseValue']
            del kwargs['exportUseValue']
        super(IntegerChoiceTypeField, self).__init__(*args, **kwargs)
        
    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return force_unicode(dict(self.flatchoices).get(value, value), strings_only=True)
    
    def value_to_int(self, obj):
        value = self._get_val_from_obj(obj)
        return int(dict(self.flatchoices).get(value, value))
    
    def json_use_value(self):
        return self.jsonUseValue
    
    def export_use_value(self):
        return self.exportUseValue
    
class JsonBitField(BitField):
    ''' use value of key when serializing as json
    '''
    jsonUseValue = True
    exportUseValue = True
    def __init__(self, *args, **kwargs):
        if 'jsonUseValue' in kwargs:
            self.jsonUseValue = kwargs['jsonUseValue']
            del kwargs['jsonUseValue']
        if 'exportUseValue' in kwargs:
            self.exportUseValue = kwargs['exportUseValue']
            del kwargs['exportUseValue']
        super(JsonBitField, self).__init__(*args, **kwargs)
        
    def json_use_value(self):
        return self.jsonUseValue
    
    def export_use_value(self):
        return self.exportUseValue  
    
    def value_to_string(self, obj):
        return " ".join(bitLabelToList(self._get_val_from_obj(obj)))
    
class JsonBitValueField(JsonBitField):
    def value_to_string(self, obj):
        return " ".join(bitToList(self._get_val_from_obj(obj)))
    

class PoolroomEquipment(models.Model):
    id = models.AutoField(primary_key=True)
    poolroom = models.ForeignKey(Poolroom, verbose_name='台球厅')
    tabletype = ChoiceTypeField(max_length=10, choices=(
            ('snooker', u'斯诺克'),
            ('pocket', u'中式八球'),
            ('nine-ball', u'花式九球'),
        ), verbose_name='球台类型')
    producer = models.CharField(max_length=20,null=True,verbose_name='球台品牌')
    quantity = models.IntegerField(max_length=8,null=True,verbose_name='数量')
    cue = models.CharField(max_length=20,null=True,verbose_name='球杆品牌')
    price = models.IntegerField(max_length=8,null=True,verbose_name='价格(元/小时)')

    class Meta:
        db_table = 'poolroomequipment'
        verbose_name = '台球厅硬件'
        verbose_name_plural = '台球厅硬件'

    def __unicode__(self):
        return u'%s - %s - %s - %s' %(self.poolroom.name, self.get_tabletype_display(), self.producer, self.cue)

    def natural_key(self):
        return {'id': self.id, 'poolroom': self.poolroom, 'tabletype': self.get_tabletype_display(),
                'producer': self.producer, 'quantity': self.quantity, 'cue': self.cue,
                'price': self.price}

class Group(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, verbose_name="群名称")
    description = models.CharField(max_length=1000, verbose_name="群简介")
    status = models.IntegerField(verbose_name=u'状态', choices=(
            (0, u'停用'),
            (1, u'正常'),
        ), default=1,)
    cardimg = models.CharField(max_length=100, verbose_name='会员卡图片',null=True)

    class Meta:
        db_table = 'fans_group'
        verbose_name = u'爱好者群'
        verbose_name_plural = u'爱好者群'

    def __unicode__(self):
        return u'%s' %(self.name)
    
    def natural_key(self):
        return {'name': self.name}

def is_expired(atime, tzinfo=pytz.timezone(TIME_ZONE)):
    if datetime.datetime.utcnow().replace(tzinfo=utc) - atime.replace(tzinfo=tzinfo) > datetime.timedelta(seconds = 5):
        return True
    return False

match_fields = ('id', 'poolroom', 'title', 'organizer', 'bonus', 'rechargeablecard', 'otherprize', 'bonusdetail', 'rule', 'starttime', 'description', 'status', 'type', 'enrollfee', 'enrollfocal')
class Match(models.Model):
    id = models.AutoField(primary_key=True)
    poolroom = models.ForeignKey(Poolroom, verbose_name='比赛/活动所在球房')
    title = models.CharField(max_length=30, verbose_name='比赛/活动名称')
    organizer = models.ForeignKey(Group, verbose_name='比赛/活动组织者, 当比赛由球房组织，请使用默认值', default=1, db_column='organizer')
    bonus = models.FloatField(null=False,verbose_name='最高现金奖金金额(元)')
    rechargeablecard = models.FloatField(null=False, verbose_name='最高充值卡奖金金额(元)')
    otherprize = models.CharField(max_length=100,null=True,blank=True,verbose_name='最高其它类别奖励')
    bonusdetail = models.TextField(null=False,verbose_name='奖金细则')
    rule = models.TextField(null=False,verbose_name='比赛规则')
    description = models.TextField(null=True,verbose_name='比赛/活动详情')
    starttime = models.DateTimeField(verbose_name='比赛/活动开始时间')
    enrollfee = models.CharField(max_length=100,null=True,verbose_name='比赛报名费/活动费用')
    enrollfocal = models.CharField(max_length=100,null=True,verbose_name='报名联系人')
    flags = BitField(flags=(
            ('groupon', u'支持团购'),
            ('coupon', u'支持用券'),
            ('redbull', u'红牛宝贝比赛'),
        ), verbose_name='特色属性')
    status = ChoiceTypeField(max_length=10, choices=(
            ('reviewing', u'等待审核'),
            ('approved', u'已审核通过'),
            ('disabled', u'已禁用'),
        ), default='approved', verbose_name=u'状态', jsonUseValue=False)
    type = IntegerChoiceTypeField(verbose_name=u'类型', choices=(
            (1, u'比赛'),
            (2, u'爱好者活动'),
        ), default=1, jsonUseValue=False)

    class Meta:
        db_table = 'match'
        verbose_name = u'比赛/爱好者活动'
        verbose_name_plural = '比赛/爱好者活动'

    def __unicode__(self):
        return u'[%s - %s] %s' %(localtime(self.starttime).strftime(DATETIME_FORMAT), self.get_type_display(), self.poolroom.name)

    def natural_key(self):
        return {'id': self.id, 'title':self.title, 'poolroom': self.poolroom.natural_key(), 'organizer': self.organizer,
                'bonus': self.bonus, 'rechargeablecard': self.rechargeablecard, 'description': self.description,
                'otherprize': self.otherprize,
                'bonusdetail': self.bonusdetail, 'rule': self.rule,
                'starttime': self.starttime, 'enrollfee': self.enrollfee,
                'enrollfocal': self.enrollfocal, 'flags': toDict(self.flags),
                'status': self.status, 'type': self.type}

    def save(self):
        super(Match, self).save()
        
    @property
    def is_expired(self):
        return is_expired(self.starttime)

    @property
    def enroll_count(self):
        return MatchEnroll.objects.filter(match=self).count()
# Using a sub table-implemented the entending of auth_user table        
# class Profile(models.Model):
#     '''
#     Additional information for User
#     '''
# #     user = models.ForeignKey(User, unique=True)  #User
#     user = models.OneToOneField(User,verbose_name="用户信息") 
#     nickname = models.TextField(max_length=200, null=False, verbose_name="昵称") # nickname
#     avatar = models.CharField(max_length=250, null=True, default='', verbose_name="头像") # address of the user logo
#     site_name = models.CharField(max_length=20, null=True, default='', verbose_name="来源") # site name 
#     gender = models.BooleanField(default=True, verbose_name="性别")
#     
# #     def __unicode__(self):
# #         return self.user.username
# #     class Meta:
# #         db_table = 'account_profile'
# def create_profile(sender, instance, created, **kwargs):
#     if created:
#         profile, created = Profile.objects\
#                             .get_or_create(user=instance)
#  
# post_save.connect(create_profile, sender=User)
# #         
def getusername(self):
    return u'%s(Tel: %s)' %(decodeunicode(self.nickname) if self.nickname is not None and self.nickname != "" else self.username,\
                            self.cellphone)

class ProfileBase(type):
    def __new__(cls, name, bases, attrs):
        module = attrs.pop('__module__')
        parents = [b for b in bases if isinstance(b, ProfileBase)]
        if parents:
            fields = []
            for obj_name, obj in attrs.items():
                if isinstance(obj, models.Field): fields.append(obj_name)
                User.add_to_class(obj_name, obj)
                User.__unicode__ = getusername
#             UserAdmin.fieldsets = list(UserAdmin.fieldsets)
#             UserAdmin.fieldsets.append((name, {'fields': fields}))
        return super(ProfileBase, cls).__new__(cls, name, bases, attrs)
        
class ProfileObject(object):
    __metaclass__ = ProfileBase

class Profile(ProfileObject):
    nickname = models.CharField(max_length=255, null=True,default='', verbose_name="昵称") # nickname
    avatar = models.CharField(max_length=250, null=True, default='', verbose_name="头像") # address of the user logo
    site_name = models.CharField(max_length=64, null=True, default='', verbose_name="来源") # site name 
    gender = models.CharField(max_length=1, default='m', null=True, verbose_name="性别")
    access_token = models.CharField(max_length=512, default='', null=True)
    expire_time = models.DateTimeField(null=True)
    refresh_token = models.CharField(max_length=512, default='', null=True)
    cellphone = models.CharField(max_length=11, null=True, blank=True, verbose_name="移动电话")
    
    def get_nickname(self):
        return decodeunicode(self.nickname)
    get_nickname.short_description = '昵称'
    
    @property
    def avatar_small(self):
        if self.avatar != '' and self.avatar.endswith('/0'):
            return self.avatar.replace('/0', '/64')
        return self.avatar
    
class MatchEnroll(models.Model):
    id = models.AutoField(primary_key=True)
    match = models.ForeignKey(Match, verbose_name='比赛')
    user = models.ForeignKey(User, verbose_name='用户')
    enrolltime = models.DateTimeField(verbose_name='报名时间')
    
    class Meta:
        db_table = 'match_enroll'
        verbose_name = '比赛报名信息'
        verbose_name_plural = '比赛报名信息'

    def __unicode__(self):
        return unicode(self.match) + " - " + (self.user.nickname if self.user.nickname is not None and self.user.nickname != "" else self.user.username)

class Challenge(models.Model):
    uuid = UUIDField(auto=True, hyphenate=True, unique=True)
    source = IntegerChoiceTypeField(verbose_name=u'发起者', choices=(
            (1, u'俱乐部'),
            (2, u'用户')
        ), default=1, jsonUseValue=False)
    poolroom = models.ForeignKey(Poolroom, db_column='poolroom', verbose_name=u'期望俱乐部')
    participant_count = IntegerChoiceTypeField(verbose_name=u'最大参与人数', choices=(
            (1, u'1人'),
            (2, u'2人'),
            (3, u'3人'),
            (4, u'4人'),
            (5, u'5人'),
        ), default=1, jsonUseValue=False)
    location = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'非球房地址')
    lat = models.DecimalField(max_digits=11,decimal_places=7,null=True,verbose_name='纬度_google地图')
    lng = models.DecimalField(max_digits=11,decimal_places=7,null=True,verbose_name='经度_google地图')
    lat_baidu = models.DecimalField(max_digits=11,decimal_places=7,null=True,verbose_name='纬度_百度地图')
    lng_baidu = models.DecimalField(max_digits=11,decimal_places=7,null=True,verbose_name='经度_百度地图')
    username = models.CharField(max_length=50, verbose_name=u'用户Id', null=True, blank=True)
    issuer = models.CharField(max_length=50, verbose_name=u'发起人Id')
    issuer_nickname = models.CharField(max_length=50, verbose_name="发起者的昵称")
    issuer_contact = models.CharField(max_length=50, verbose_name="发起者的联系方式")
    starttime = models.DateTimeField(verbose_name='开始时间')
    expiretime = models.DateTimeField(verbose_name='过期时间')
    level = ChoiceTypeField(max_length=12, choices=(
            ('amateur', u'初级球友'),
            ('professional', u'专业高手'),
            ('master', u'职业球手'),
            ('companion', u'陪练')
        ), verbose_name='发起者水平')
    tabletype = ChoiceTypeField(max_length=10, choices=(
            ('snooker', u'斯诺克'),
            ('pocket', u'中式八球'),
            ('nine-ball', u'花式九球'),
            ('any', u'不限')
        ), verbose_name='球台类型')
    rule = models.CharField(max_length=50, verbose_name="比赛方式")
    status = ChoiceTypeField(max_length=7, choices=(
            ('waiting', u'等待匹配'),
            ('matched', u'已经匹配'),
            ('expired', u'已经过期'),
            ('closed', u'已经关闭'),
        ), default='waiting', verbose_name='状态', jsonUseValue=False)
    group = models.ForeignKey(Group, verbose_name='约球来源,默认值1代表pktaiqiu网站', db_column='group', default=1)
    geolocation = GeohashField(blank=True)
    
    objects = GeoManager()
    
    def save(self):
        self.geolocation = (self.lat, self.lng)
        super(Challenge, self).save()
    
    def __init__(self, *args, **kwargs):
        super(Challenge, self).__init__(*args, **kwargs)
        if self.lat is not None:
            self.geolocation = (self.lat, self.lng)

    @property
    def local_expiretime(self):
        ue = self.expiretime.replace(tzinfo=utc)
        return ue.astimezone(pytz.timezone(settings.TIME_ZONE))
    
    @property
    def tabletype_display(self):
        return self.get_tabletype_display()
    
    @property
    def level_display(self):
        return self.get_level_display()

    @property
    def is_expired(self):
        return is_expired(self.expiretime, utc) or self.status == 'expired'
    
    @property
    def isMatched(self):
        if self.enroll_count >= self.participant_count or self.status == 'matched':
            return True
        return False
    
    @property
    def availableTime(self):
        delta = self.expiretime.replace(tzinfo=utc) - datetime.datetime.utcnow().replace(tzinfo=utc)
        s = delta.seconds
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        return (hours, minutes)

    @property
    def participants(self):
        return ChallengeApply.objects.filter(challenge=self).order_by("applytime")

    @property
    def enroll_count(self):
        return self.participants.count()
    
    @property
    def is_readonly(self):
        rt = self.is_expired or self.status != 'waiting' or self.enroll_count >= self.participant_count
        return rt
    
    class Meta:
        db_table = 'challenge'
        verbose_name = '约赛'
        verbose_name_plural = '约赛'        
        
    def __unicode__(self):
        return u'%s - %s - %s - %s - %s - %s' %(self.issuer_nickname, self.starttime, self.get_level_display(), self.get_tabletype_display(), self.rule, self.get_status_display())
   
class ChallengeApply(models.Model):
    challenge = models.ForeignKey(Challenge, verbose_name='约赛')
    user = models.ForeignKey(User, verbose_name='用户')
    applytime = models.DateTimeField(verbose_name='申请应战时间')
    status = ChoiceTypeField(max_length=10, choices=(
            ('submitted', u'已提交，等待俱乐部确认'),
            ('accepted', u'审核通过'),
            ('rejected', u'审核拒绝'),
        ), default='submitted', verbose_name='状态') 
    
    class Meta:
        db_table = 'challenge_apply'
        verbose_name = '约赛应战'
        verbose_name_plural = '约赛应战'
        unique_together = ('challenge', 'user',)
        
    def __unicode__(self):
        return u'[%s]%s(%s)已应战 %s' %(self.get_status_display(), \
                                     (self.user.nickname if self.user.nickname is not None and self.user.nickname != "" else self.user.username),\
                                     self.applytime, unicode(self.challenge))

    @property
    def status_display(self):
        return self.get_status_display()
    
    def verbose_username(self):
        return "%s <br/>Email: %s<br/>Tel: %s" % ((self.user.nickname if self.user.nickname is not None and self.user.nickname != "" else self.user.username), self.user.email, self.user.cellphone)
    verbose_username.short_description = u'用户详细信息'
    verbose_username.allow_tags = True
        
class PoolroomUser(models.Model):
    id = models.AutoField(primary_key=True)
    poolroom = models.ForeignKey(Poolroom, verbose_name='台球俱乐部')
    group = models.ForeignKey(Group, verbose_name='爱好者群(当管理类型是俱乐部管理员时，请使用默认值)', default=0)
    user = models.ForeignKey(User, verbose_name='用户名')
    type = IntegerChoiceTypeField(verbose_name=u'类型', choices=(
            (1, u'俱乐部管理员'),
            (2, u'活动群组织者')
        ), default=1)
    
    class Meta:
        db_table = 'poolroom_user'
        verbose_name = '俱乐部用户管理'
        verbose_name_plural = '俱乐部用户管理'
        
    def __unicode__(self):
        return u'\'%s%s\' %s:%s' %(self.poolroom, (u'' if self.type == 2 else u'合作群"%s"' %(self.group.name)), (u'管理员' if self.type == 1 else u'群组织者'), \
                                     (self.user.nickname if self.user.nickname is not None and self.user.nickname != "" else self.user.username))
    def verbose_user(self):
            return "%s <br/>Email: %s<br/>Tel: %s" % ((self.user.nickname if self.user.nickname is not None and self.user.nickname != "" else self.user.username), self.user.email, self.user.cellphone)
    verbose_user.short_description = u'俱乐部管理员详细信息'
    verbose_user.allow_tags = True  

class PoolroomUserApply(models.Model):
    id = models.AutoField(primary_key=True)
    poolroom = models.ForeignKey(Poolroom, verbose_name='台球俱乐部')
    poolroomname_userinput = models.CharField(max_length=50, null=True, default=True, verbose_name="用户输入俱乐部名")
    user = models.ForeignKey(User, verbose_name='申请用户')
    realname = models.CharField(max_length=10, verbose_name="真实姓名")
    cellphone = models.CharField(max_length=15, verbose_name="手机号码")
    email = models.CharField(max_length=20, verbose_name="电子邮箱")
    justification = models.CharField(max_length=500, verbose_name="申请理由")
    applytime = models.DateTimeField(verbose_name='申请时间')
    status = ChoiceTypeField(max_length=10, choices=(
            ('submitted', u'已提交，等待确认'),
            ('accepted', u'审核通过'),
            ('rejected', u'审核拒绝'),
        ), default='submitted', verbose_name='状态') 
    
    class Meta:
        db_table = 'poolroom_user_application'
        verbose_name = '俱乐部管理员申请'
        verbose_name_plural = '俱乐部管理员申请'
        
    def __unicode__(self):
        return u'\'%s\' 申请者用户名:%s' %(self.poolroom, \
                                     (self.user.nickname if self.user.nickname is not None and self.user.nickname != "" else self.user.username))
    def verbose_user(self):
            return "%s <br/>Email: %s<br/>Tel: %s" % ((self.user.nickname if self.user.nickname is not None and self.user.nickname != "" else self.user.username), self.user.email, self.user.cellphone)
    verbose_user.short_description = u'俱乐部管理员申请表单的详细信息'
    verbose_user.allow_tags = True  

class Coupon(models.Model):
    id = models.AutoField(primary_key=True)
    poolroom = models.ForeignKey(Poolroom, verbose_name='台球俱乐部')
    title = models.CharField(max_length=50, verbose_name='折扣标题')
    description = models.CharField(max_length=200, verbose_name='折扣描述')
    discount = models.IntegerField(max_length=3, verbose_name='折扣率')
    startdate = models.DateField(verbose_name='开始日期')
    enddate = models.DateField(verbose_name='结束日期', null=True, blank=True)
    url = models.CharField(max_length=100, verbose_name='折扣链接')
    type = IntegerChoiceTypeField(verbose_name=u'折扣类型', choices=(
            (1, u'团购'),
        ), default=1, jsonUseValue=False)
    status = IntegerChoiceTypeField(verbose_name=u'状态', choices=(
            (1, u'有效'),
            (2, u'过期'),
            (3, u'失效'),
            (4, u'无效')
        ), default=1, jsonUseValue=False)
    
    def __unicode__(self):
        return u'[%s] \'%s\'-%s(从%s至%s)' %(self.get_type_display(), self.poolroom, self.title, self.startdate, self.enddate)
                
    class Meta:
        db_table = 'coupon'
        verbose_name = '折扣信息'
        verbose_name_plural = '折扣信息'   
        
class WechatActivityManager(models.Manager):
    def create_activity(self, userid, event, keyword, message, recivedtime, reply, target = 1):
        activity = self.create(userid=userid, eventtype=event, keyword=keyword, message=message, receivedtime=recivedtime, reply=reply, target=target)
        # do something with the book
        return activity
    
class WechatActivity(models.Model):
    id = models.AutoField(primary_key=True)
    userid = models.CharField(max_length=30, verbose_name='用户id')
    eventtype = ChoiceTypeField(max_length=10, choices=(
            ('text', u'文本消息'),
            ('image', u'图片消息'),
            ('location', u'地理位置消息'),
            ('link', u'链接消息'),
            ('event', u'事件推送'),
        ), verbose_name='消息类型')
    keyword = CharField(max_length=40, verbose_name='消息类型关键词')
    message = CharField(max_length=500, verbose_name='消息内容')
    receivedtime = models.DateTimeField(verbose_name='发送时间')
    reply = CharField(max_length=500, null=True, blank=True, verbose_name='自定义回复概要')
    target = IntegerChoiceTypeField(verbose_name=u'目标公众帐号', default=1)
    
    
    objects = WechatActivityManager()
    
    def __unicode__(self):
        localtz = pytz.timezone(settings.TIME_ZONE)
        return u'[%s][%s] 用户\'%s\' %s发送 %s - %s' %(self.get_target_display(), self.eventtype, self.userid, self.receivedtime.astimezone(localtz), 
                                               self.get_eventtype_display(), self.message)
        
    def get_userid_display(self):
        try:
            user = User.objects.get(username=self.userid)
            return user.nickname.decode('unicode_escape')
        except User.DoesNotExist:
            return self.userid
        
    def get_target_display(self):
        if self.target == 1:
            return u'我为台球狂'
        elif self.target == 0:
            return u'我为台球狂--服务号'
        try:
            return Group.objects.get(id=self.target).name
        except:
            return "unknown target"
      
    class Meta:
        db_table = 'wechat_activity'
        verbose_name = '微信用户互动信息'
        verbose_name_plural = '微信用户互动信息'
        
class Event(models.Model):
    id = models.AutoField(primary_key=True)
    year = models.IntegerField(verbose_name='年份')
    month = models.IntegerField(verbose_name='月份')
    titleabbrev = models.CharField(max_length=30, null=True, blank=True, verbose_name='活动英文缩写(用于url)')
    title = models.CharField(max_length=30, null=True, blank=True, verbose_name='标题(用于微信等)')
    description = models.CharField(max_length=255, verbose_name='活动简介(用于微信等)')
    picAD = models.CharField(max_length=255, null=True, blank=True, verbose_name='活动宣传图片(用于微信等)')
    pagename = models.CharField(max_length=50, verbose_name='实现页面文件名')
    startdate = models.DateField(verbose_name='开始日期(包含)')
    enddate = models.DateField(verbose_name='结束日期(包含)')
    
    def __unicode__(self):
        return u'[%s-%s-%s] %s(%s)' %(self.year, self.month, self.titleabbrev, self.title, self.description)
    
    class Meta:
        db_table = 'event'
        verbose_name = '推广活动'
        verbose_name_plural = '推广活动'
        
class EventCode(models.Model):
    id = models.AutoField(primary_key=True)
    poolroom = models.ForeignKey(Poolroom, verbose_name='台球厅')
    event = models.ForeignKey(Event, verbose_name='推广活动')
    userid = models.CharField(max_length=30, verbose_name='用户id')
    createdtime = models.DateTimeField(verbose_name='创建时间', default=datetime.datetime.utcnow().replace(tzinfo=utc))
    chargecode = models.CharField(max_length=10, verbose_name='消费唯一码', default=generator())
    usedtime = models.DateTimeField(verbose_name='创建时间', blank=True, null=True)
    used = models.BooleanField(verbose_name='使用没有', default=False)
    
    class Meta:
        db_table = 'eventcode'
        verbose_name = '推广活动消费码'
        verbose_name_plural = '推广活动消费码'

class Membership(models.Model):
    id = models.AutoField(primary_key=True)
    userid = models.IntegerField(default=0, verbose_name='站类用户')
    wechatid = models.CharField(max_length=30, verbose_name='wechat用户id')
    targetid = models.ForeignKey(Group, verbose_name='会员组织者(我为台球狂/俱乐部/爱好者群)', default=1, db_column='target_group')
    joindate = models.DateTimeField(verbose_name='加入时间', default=datetime.datetime.utcnow().replace(tzinfo=utc))
    memberid = models.CharField(max_length=20, verbose_name='会员唯一码', default=generator(11, string.digits))
    name = models.CharField(max_length=20, verbose_name='真实姓名')
    gender = IntegerChoiceTypeField(verbose_name=u'性别', choices=(
            (1, u'男'),
            (2, u'女'),
        ), default=1, jsonUseValue=False)
    cellphone = models.CharField(max_length=11, verbose_name='手机号码')
    
    def __unicode__(self):
        localtz = pytz.timezone(settings.TIME_ZONE)
        return u'[%s][%s] %s(%s) -- %s' %(self.targetid.name, self.get_gender_display(), self.name, self.memberid, self.joindate.astimezone(localtz))
    
    class Meta:
        db_table = 'membership'
        verbose_name = '会员资料'
        verbose_name_plural = '会员资料'
        
class WechatCredential(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, verbose_name='微信号')
    appid = models.CharField(max_length=32, verbose_name='AppId')
    secret = models.CharField(max_length=64, verbose_name='Secret')
    
    class Meta:
        db_table = 'wechat_credential'
        verbose_name = '微信开发者凭证'
        verbose_name_plural = '微信开发者凭证'

class PayAccount(models.Model):
    Alipay = 1
    Nowpay = 2
    TYPES = (
            (Alipay, u'Alipay'),
            (Nowpay, u'Nowpay'),
        )
    id = models.AutoField(primary_key=True)
    pid = models.CharField(max_length=16, verbose_name='Partner ID')
    key = models.CharField(max_length=64, verbose_name='Key')
    name = models.CharField(max_length=32, verbose_name='账号名')
    email = models.CharField(max_length=64, verbose_name='帐号邮箱')
    type = IntegerChoiceTypeField(verbose_name=u'帐号类型', choices=TYPES, default=1)
    
    def __unicode__(self):
        return u"%s:%s" %(self.get_type_display(), self.name)
    
    class Meta:
        db_table = 'payaccount'
        verbose_name = '交易账户信息'
        verbose_name_plural = '交易账户信息'
    
class CurrencyField(models.DecimalField):
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, verbose_name=None, name=None, **kwargs):
        kwargs = {key: value for key, value in kwargs.items() 
             if key not in ('decimal_places', 'max_digits')}
        super(CurrencyField, self). __init__(
        verbose_name=verbose_name, name=name, max_digits=10,
        decimal_places=2, **kwargs)

    def to_python(self, value):
        try:
            return super(CurrencyField, self).to_python(value).quantize(Decimal("0.01"))
        except AttributeError:
            return None
        
class Goods(models.Model):
    sku = models.CharField(max_length=32, verbose_name='商品sku', unique=True)
    name = models.CharField(max_length=256, verbose_name='商品名称')
    description = models.CharField(max_length=512, verbose_name='描述')
    price = CurrencyField(verbose_name='价格(元)')
    type = IntegerChoiceTypeField(verbose_name=u'类别', choices=(
            (1, u'电子卡'),
            (2, u'预约'),
        ), default=1)
    state = IntegerChoiceTypeField(verbose_name=u'状态', choices=(
            (1, u'可购买'),
            (2, u'已下架'),
            (3, u'已售完'),
        ), default=1)
    
    def __unicode__(self):
        return u'[%s] %s(%s元) -- %s' %(self.get_type_display(), self.name, self.price, self.get_state_display())
    
    def natural_key(self):
        return {'sku': self.sku, 'price': self.price, 'id': self.sku}
        
    class Meta:
        db_table = 'goods'
        verbose_name = '可交易商品'
        verbose_name_plural = '可交易商品'
          
class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    payaccount = models.ForeignKey(PayAccount, verbose_name='交易账户', db_column='payaccount')
    subject = models.CharField(max_length=256, verbose_name='商品名称')
    user = models.ForeignKey(User, verbose_name='用户标识', db_column='uid')
    goods = models.ForeignKey(Goods, verbose_name='商品唯一id', db_column='goods')
    fee = CurrencyField(verbose_name='交易金额')
    createdDate = models.DateTimeField(verbose_name='交易生成时间')
    paidDate = models.DateTimeField(verbose_name='交易付款时间', null=True, blank=True)
    closedDate = models.DateTimeField(verbose_name='交易关闭时间', null=True, blank=True)
    validUntilDate = models.DateTimeField(verbose_name='有效期截止时间(null代表一直有效)', null=True, blank=True)
    paytradeNum = models.CharField(max_length=64, verbose_name='交易号')
    tradeStatus = models.CharField(max_length=32, verbose_name='交易状态')
    notifyid = models.CharField(max_length=128, verbose_name='通知校验ID')
    buyerEmail = models.CharField(max_length=100, verbose_name='买家Email')
    buyeid = models.CharField(max_length=30, verbose_name='买家帐号')
    state = IntegerChoiceTypeField(verbose_name=u'状态', choices=(
            (1, u'等待付款'),
            (2, u'已成功'),
            (3, u'已取消'),
            (4, u'已过期'),
            (5, u'已完成')
        ), default=1, jsonUseValue=True)
    
    @property
    def paymentExpired(self):
        if self.state != 1 or \
            (self.validUntilDate and self.validUntilDate.replace(tzinfo=utc) - datetime.datetime.utcnow().replace(tzinfo=utc) < datetime.timedelta(seconds = 1)):
            return True
        return False
    
    @property
    def tradeNum(self):
        return "YY" + generator(6, string.ascii_uppercase) + '{:08d}'.format(self.id)
        
    def natural_key(self):
        return {'tradenum': self.tradeNum, 'goods': self.goods.natural_key(), 'fee': self.fee, 'tradeStatus': self.tradeStatus,
                'state': int(self.state)}
        
    def __unicode__(self):
        return u"[%s] %s" %(self.payaccount, self.paytradeNum)
        
    class Meta:
        db_table = 'transaction'
        verbose_name = '交易信息'
        verbose_name_plural = '交易信息'
        
assistant_fields = ('uuid', 'nickname', 'birthday', 'gender', 'height', 'figure', 'haircolor', 'occupation',
                    'language', 'interest', 'food', 'drinks', 'scent', 'dress', 'nationality',
                    'birthplace', 'constellation', 'measurements', 'experience', 'favoriteplayers', 'bestperformance',
                    'selfintroduce')
class Assistant(models.Model):
    uuid = UUIDField(auto=True, hyphenate=True, unique=True)
    name = models.CharField(max_length=24, verbose_name="真实姓名")
    nickname = models.CharField(max_length=24, verbose_name="昵称")
    birthday = models.DateField(verbose_name="生日")
    gender = IntegerChoiceTypeField(verbose_name=u'性别', choices=(
            (1, u'女'),
            (2, u'男'),
        ), default=1, jsonUseValue=False)
    
    nationality = models.CharField(max_length=16, verbose_name="国籍")
    birthplace = models.CharField(max_length=24, verbose_name="籍贯")
    constellation = models.CharField(max_length=8, verbose_name="星座")
    
    height = models.IntegerField(verbose_name="身高(cm)")
    measurements = models.CharField(verbose_name="三围", max_length=24)
    haircolor = ChoiceTypeField(max_length=16, choices=(
            ('blank', u'黑发色'),
            ('brown', u'褐发色'),
            ('blond', u'金发色'),
            ('auburn', u'赤褐发色'),
            ('chestnut', u'栗发色'),
            ('ginger/red', u'红发色'),
            ('gray-white', u'灰白发色'),
        ), verbose_name='头发颜色', jsonUseValue=False, exportUseValue=True)
    pubichair = models.CharField(verbose_name='阴毛', blank=True, max_length=64)
    
    occupation = models.CharField(verbose_name='职业', max_length=24)
    language = JsonBitField(flags=(
            ('mandarin', u'普通话'),
            ('english', u'英语'),
            ('french', u'法语'),
            ('japanese', u'日语'),
            ('geman', u'德语'),
            ('cantonese', u'粤语'),
        ), verbose_name='语言', jsonUseValue=False, exportUseValue=True)
    interest = models.CharField(verbose_name='个人爱好', max_length=64)
    food = models.CharField(verbose_name='喜好的食物', max_length=64)
    drinks = models.CharField(verbose_name='喜好的饮品', max_length=64)
    scent = models.CharField(verbose_name='气味', max_length=64)
    dress = models.CharField(verbose_name='穿着风格', max_length=64)
    figure = models.CharField(verbose_name='个性', max_length=64)
    
    experience = models.IntegerField(verbose_name="球龄(年)")
    favoriteplayers = models.CharField(verbose_name="喜爱的台球选手", max_length=64)
    selfintroduce = models.CharField(verbose_name="自我介绍", max_length=1024)
    bestperformance = models.CharField(verbose_name="最佳清台记录", max_length=128)

    pageview = models.BigIntegerField(default=0, verbose_name="浏览次数")
    
    state = IntegerChoiceTypeField(verbose_name=u'状态', choices=(
            (1, u'有效'),
            (2, u'失效'),
            (8, u'禁用'),
        ), default=1, exportUseValue=True)
    
    order = models.IntegerField(verbose_name='助教排序(默认大的在前)', default=100)
    
    _coverimage = None
    @property
    def coverimage(self):
        if self._coverimage == None:
            try:
                self._coverimage = AssistantImage.objects.filter(assistant=self).filter(iscover=True).get().imagepath.name
            except AssistantImage.DoesNotExist:
                pass
        return self._coverimage
    
    @property
    def images(self):
        return AssistantImage.objects.filter(assistant=self)
    
    class Meta:
        db_table = 'assistant'
        verbose_name = '助教个人资料'
        verbose_name_plural = '助教个人资料'
        
    def __unicode__(self):
        return u"[%s] %s(%s) - %s" %(self.get_gender_display(), self.nickname, self.name, self.birthday)
    
    def natural_key(self):
        coverimage = None
        if self.coverimage is not None:
            coverimage = "%s%s" %(settings.MEDIA_URL[:-1], self.coverimage)
        elif len(self.images()) > 0:
            coverimage = "%s%s" %(settings.MEDIA_URL[:-1], self.images[0].imagepath)
        return {'uuid': str(self.uuid), 'nickname': self.nickname, 'coverimage': coverimage, 'height': self.height,
                'birthday': self.birthday, 'occupation': self.occupation}
        
UPLOAD_TO_ASSISTANT = UPLOAD_TO + 'assistant/'
assistantimage_fields = ('imagepath', 'iscover')
class AssistantImage(models.Model):
    assistant = models.ForeignKey(Assistant, verbose_name='助教')
    imagepath = models.ImageField(verbose_name=u'选择本地图片/图片路径', max_length=250, upload_to=UPLOAD_TO_ASSISTANT, 
                                  storage=ImageStorage())
    description = models.CharField(verbose_name=u'图片说明', null=True, blank=True, max_length=50)
    iscover = models.BooleanField(verbose_name=u'是否是封面图片', default=False)
    status = IntegerChoiceTypeField(verbose_name=u'状态', choices=(
            (0, u'不可用'),
            (1, u'可用'),
        ), default=1, exportUseValue=True)
    
    class Meta:
        db_table = 'assistant_images'
        verbose_name = '助教图片'
        verbose_name_plural = '助教图片'
        
    def imagetag(self):
        return u'<img src="%s%s" />' %(MEDIA_URL, self.imagepath)
    imagetag.short_description = u'图片预览'
    imagetag.allow_tags = True

    def __unicode__(self):
        return u"[封面-%s] %s-%s" %((u"Y" if self.iscover else u"N"), unicode(self.assistant), self.description)
    
    __imagepath = None
    
    def __init__(self, *args, **kwargs):
        super(AssistantImage, self).__init__(*args, **kwargs)
        self.__imagepath = self.imagepath
    
    def save(self):
        super(AssistantImage, self).save()
        
        if self.imagepath != self.__imagepath:
            # avoid import issue in local env
            # https://github.com/BaiduAppEngine/bae-python-sdk/issues/1
            try:
                from bae_image.image import BaeImage
                img = BaeImage(BAE_IMAGE['key'], BAE_IMAGE['secret'], BAE_IMAGE['host'])
                albumstorage = ImageStorage()
                path = str(self.imagepath)
                import base64
                for height in ESCORT_HEIGHT:
                    img.clearOperations()
                    img.setSource(MEDIA_URL + path)
                    img.setZooming(BaeImage.ZOOMING_TYPE_HEIGHT, height)
                    ret = img.process()
                    body = ret['response_params']['image_data']
                
                    newpath = getThumbnailPath(path, height, 'h')
                    albumstorage.saveToBucket(newpath, base64.b64decode(body))
            except ImportError:
                pass
        self.__imagepath = self.imagepath
        
class AssistantLikeStats(models.Model):
    assistant = models.ForeignKey(Assistant, verbose_name='助教')
    user = models.ForeignKey(User, verbose_name='用户')
    isLiked = models.BooleanField(verbose_name='是否喜欢', default=True)
    lastUpdated = models.DateTimeField(verbose_name='最后更新日期')
    
    class Meta:
        db_table = 'assistant_likes'
        verbose_name = '赞助教统计'
        verbose_name_plural = '赞助教统计'
        unique_together = ('assistant', 'user',)
        index_together = [
            ["assistant", "isLiked"],
        ]
        
assistantoffer_fields = ('assistant', 'poolroom', 'price')
assistantoffer_fields_2 = ('poolroom', 'price', 'starttime', 'endtime', 'priceDescription', 'extraService')
class AssistantOffer(models.Model):
    assistant = models.ForeignKey(Assistant, verbose_name="助教", related_name="offer")
    poolroom = models.IntegerField(verbose_name="预约的球房", blank=True)
    price = models.IntegerField(verbose_name="价钱(元/小时)")
    day = JsonBitValueField(flags=(
            ('monday', u'周一'),
            ('tuesday', u'周二'),
            ('wendesday', u'周三'),
            ('thursday', u'周四'),
            ('friday', u'周五'),
            ('saturday', u'周六'),
            ('sunday', u'周日'),
        ), verbose_name='星期几', jsonUseValue=True, exportUseValue=True)
    starttime = models.TimeField(verbose_name="开始时间")
    endtime = models.TimeField(verbose_name="结束时间")
    priceDescription = models.CharField(max_length=200, verbose_name="报价说明", blank=True)
    extraService = models.CharField(max_length=200, verbose_name="额外服务说明", blank=True)
    status = IntegerChoiceTypeField(verbose_name=u'状态', choices=(
            (0, u'失效'),
            (1, u'有效'),
        ), default=1, exportUseValue=True)
    
    class Meta:
        db_table = 'assistant_offer'
        verbose_name = '助教报价'
        verbose_name_plural = '助教报价'
        
    def __unicode__(self):
        poolroomname = ''
        if self.poolroom is not None:
            poolroomname = Poolroom.objects.get(id=self.poolroom)
        return u"[%s] %s %s元/小时 (%s-%s)" %(self.assistant.nickname, poolroomname,  self.price, self.starttime, self.endtime)
    
        
assistant_appointment_fields = ('assistant', 'poolroom', 'starttime', 'endtime', 'duration', 'price', 'createdDate',
            'state')
class AssistantAppointment(models.Model):
    assistant = models.ForeignKey(Assistant, verbose_name="助教")
    user = models.ForeignKey(User, verbose_name="用户")
    poolroom = models.IntegerField(verbose_name="预约的球房", blank=True)
    goods = models.ForeignKey(Goods, verbose_name="商品id")
    transaction = models.ForeignKey(Transaction, verbose_name="交易订单", unique=True)
    starttime = models.DateTimeField(verbose_name="预订开始时间")
    endtime = models.DateTimeField(verbose_name="预订结束时间")
    duration = models.IntegerField(verbose_name="时长(小时)")
    price = CurrencyField(verbose_name="价钱(元/小时)")
    createdDate = models.DateTimeField(verbose_name="预约创建时间")
    chargeCode = models.CharField(max_length=12, verbose_name="消费代码", default=generator(6))
    state = IntegerChoiceTypeField(verbose_name=u'状态', choices=(
            (1, u'等待付款'),
            (2, u'等待确认'),
            (4, u'等待退款'),
            (8, u'交易取消'),
            (16, u'交易关闭'),
            (32, u'已确认'),
            (256, u'交易完成'),
        ), default=1, jsonUseValue=True)  
    
    class Meta:
        db_table = 'assistant_appoinment'
        verbose_name = '助教预约详情'
        verbose_name_plural = '助教预约详情'
        index_together = [
            ["chargeCode", "state"]
        ]
        
    def __unicode__(self):
        return u"[%s] %s %s" %(self.get_state_display(), self.user, self.goods.name)
    
    def __toDict(self):
        poolroom = Poolroom.objects.get(id=self.poolroom)
        return {'assistant_name': self.assistant.nickname, 'starttime': localtime(self.starttime).strftime(DATETIME_FORMAT), 'endtime': localtime(self.endtime).strftime(DATETIME_FORMAT),
                'duration': self.duration, 'price': int(self.price), 'poolroom_name': poolroom.name, 'poolroom_address': poolroom.address,
                'payment': int(self.transaction.fee), 'user_nickname': decodeunicode(self.user.nickname), 'user_cellphone': self.user.cellphone,
                'timestamp': int(time.time())}

    __original_state = None

    def __init__(self, *args, **kwargs):
        super(AssistantAppointment, self).__init__(*args, **kwargs)
        self.__original_state = int(self.state)
        
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if int(self.state) != self.__original_state:
            orderdict = self.__toDict()
            if int(self.state) == 32:
                orderdict['method'] = 'billiards.messages.assistant.orderConfirmationMsg'
            elif int(self.state) == 2:
                orderdict['method'] = 'billiards.messages.assistant.orderArrival'
                try:
                    au = AssistantUser.objects.get(assistant=self.assistant)
                    notification_msg(au.user.cellphone, simplejson.dumps(orderdict))
                except AssistantUser.DoesNotExist:
                    logger.warn(u'Can not find the associated user for assistant \'%s\'.' %(self.assistant))
                orderdict['method'] = 'billiards.messages.assistant.orderPaySuccess'
            elif int(self.state) == 256:
                orderdict['method'] = 'billiards.messages.assistant.orderComplete'
            if 'method' in orderdict:
                notification_msg(self.user.cellphone, simplejson.dumps(orderdict))
        super(AssistantAppointment, self).save(force_insert, force_update, *args, **kwargs)
        self.__original_state = int(self.state)
    
class AssistantUser(models.Model):
    assistant = models.ForeignKey(Assistant, verbose_name="助教")
    user = models.ForeignKey(User, verbose_name="用户")
    
    class Meta:
        db_table = 'assistant_user'
        verbose_name = '助教用户管理'
        verbose_name_plural = '助教用户管理'
        unique_together = ('assistant', 'user',)
        
    def __unicode__(self):
        return u"助教(%s) 对应用户 '%s'" %(self.assistant.nickname, self.user)

class BcmsMessage(models.Model):
    lastMsgId = models.BigIntegerField(verbose_name='最后的消息id')
    
    class Meta:
        db_table = 'bcms'
        verbose_name = 'Bcms消息'
        verbose_name_plural = 'Bcms消息'

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^billiards\.models\.ChoiceTypeField"])
    add_introspection_rules([], ["^billiards\.models\.IntegerChoiceTypeField"])
    add_introspection_rules([], ["^billiards\.models\.JsonBitField"])
    add_introspection_rules([], ["^billiards\.models\.CurrencyField"])
except:
    pass
