# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2013年10月21日

@author: kane
'''

from django.db import models
from django.utils.timezone import localtime, pytz
from bitfield import BitField
from django.utils.encoding import force_unicode
from django.contrib.auth.models import User
from billiards.storage import ImageStorage
from billiards.settings import UPLOAD_TO, TIME_ZONE, MEDIA_ROOT, BAE_IMAGE,\
    THUMBNAIL_WIDTH
import datetime
from django.core.serializers.json import Serializer as JsonSerializer 
from django.utils.encoding import is_protected_type 
import os
from django.db.models.query_utils import Q
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
import sys
from django.db.models.fields import CharField
from billiards import settings
from billiards.id import generator

def toDict(bitfield):
    flag_dict = {}
    for f in bitfield:
        flag_dict[f[0]] = f[1]
    return flag_dict

poolroom_fields = ('id', 'name', 'address', 'tel', 'lat_baidu', 'lng_baidu', 'flags', 'businesshours', 'size', 'rating')

def getCouponCriteria():
    datefmt = "%Y-%m-%d"
    starttime = datetime.datetime.today()
    return Q(startdate__lte=starttime.strftime(datefmt)) & \
        (Q(enddate__isnull=True) | Q(enddate__gte=starttime.strftime(datefmt))) & \
        Q(status=1)
        
class Poolroom(models.Model):
    id = models.AutoField(primary_key=True)
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
        ), verbose_name='特色属性')
    businesshours = models.CharField(max_length=60,null=True,verbose_name='营业时间')
    size = models.IntegerField(max_length=8,null=True,verbose_name='球馆面积(平米)')
    rating = models.IntegerField(max_length=2,null=True,verbose_name='球房总评分')
    review = models.CharField(max_length=255,null=True,blank=True,verbose_name='球房点评')

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
        return {'id': self.id, 'name': self.name, 'lat': self.lat_baidu, 'lng': self.lng_baidu,
                'businesshours': self.businesshours, 'size': self.size,
                'address': self.address, 'flags': toDict(self.flags), 'rating': self.rating,
                'images': images}
        
    @property
    def images(self):
        return PoolroomImage.objects.filter(Q(poolroom=self) & Q(status=1))
    
    @property
    def coupons(self):
        return Coupon.objects.filter(Q(poolroom=self) & getCouponCriteria())

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
        return u'<img src="%s%s" />' %(MEDIA_ROOT, self.imagepath)
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
                    img.setSource(MEDIA_ROOT + path)
                    img.setZooming(BaeImage.ZOOMING_TYPE_WIDTH, width)
                    ret = img.process()
                    body = ret['response_params']['image_data']
                
                    newpath = PoolroomImage.getThumbnailPath(path, width)
                    albumstorage.saveToBucket(newpath, base64.b64decode(body))
            except ImportError:
                pass
        self.__imagepath = self.imagepath

    @staticmethod
    def getThumbnailPath(path, width):
        fileName, fileExtension = os.path.splitext(path)
        return "%s-w%s%s" %(fileName, width, fileExtension)

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
    def __init__(self, *args, **kwargs):
        if 'jsonUseValue' in kwargs:
            self.jsonUseValue = kwargs['jsonUseValue']
            del kwargs['jsonUseValue']
        super(ChoiceTypeField, self).__init__(*args, **kwargs)
        
    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        if sys._getframe(2).f_code.co_name == 'serialize':
            return value
        return force_unicode(dict(self.flatchoices).get(value, value), strings_only=True)
    
    def json_use_value(self):
        return self.jsonUseValue

class IntegerChoiceTypeField(models.IntegerField):
    ''' use value of key when serializing as json
    '''
    jsonUseValue = True
    def __init__(self, *args, **kwargs):
        if 'jsonUseValue' in kwargs:
            self.jsonUseValue = kwargs['jsonUseValue']
            del kwargs['jsonUseValue']
        super(IntegerChoiceTypeField, self).__init__(*args, **kwargs)
        
    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return force_unicode(dict(self.flatchoices).get(value, value), strings_only=True)
    
    def value_to_int(self, obj):
        value = self._get_val_from_obj(obj)
        return int(dict(self.flatchoices).get(value, value))
    
    def json_use_value(self):
        return self.jsonUseValue

class PoolroomEquipment(models.Model):
    id = models.AutoField(primary_key=True)
    poolroom = models.ForeignKey(Poolroom, verbose_name='台球厅')
    tabletype = ChoiceTypeField(max_length=10, choices=(
            ('snooker', u'斯诺克 snooker'),
            ('pocket', u'十六彩(美式落袋)'),
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

    class Meta:
        db_table = 'fans_group'
        verbose_name = u'爱好者群'
        verbose_name_plural = u'爱好者群'

    def __unicode__(self):
        return u'%s' %(self.name)
    
    def natural_key(self):
        return {'name': self.name}

class DisplayNameJsonSerializer(JsonSerializer): 

    def handle_field(self, obj, field): 
        value = field._get_val_from_obj(obj) 

        #If the object has a get_field_display() method, use it. 
        display_method = "get_%s_display" % field.name 
        if  hasattr(field, 'json_use_value') and getattr(field, 'json_use_value')() == False:
            self._current[field.name] = value
        elif hasattr(obj, display_method): 
            self._current[field.name] = getattr(obj, display_method)() 
        # Protected types (i.e., primitives like None, numbers, dates, 
        # and Decimals) are passed through as is. All other values are 
        # converted to string first. 
        elif is_protected_type(value): 
            self._current[field.name] = value 
        else: 
            self._current[field.name] = field.value_to_string(obj) 
            
def is_expired(atime):
    if datetime.datetime.utcnow().replace(tzinfo=pytz.timezone(TIME_ZONE)) - atime.replace(tzinfo=pytz.timezone(TIME_ZONE)) > datetime.timedelta(seconds = 5):
        return True
    return False

match_fields = ('id', 'poolroom', 'title', 'organizer', 'bonus', 'rechargeablecard', 'otherprize', 'bonusdetail', 'rule', 'starttime', 'description', 'status', 'type', 'enrollfee')
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
        return u'[%s - %s] %s' %(localtime(self.starttime).strftime("%Y-%m-%d %H:%M:%S"), self.get_type_display(), self.poolroom.name)

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
    return self.nickname if self.nickname is not None and self.nickname != "" else self.username

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
    nickname = models.TextField(max_length=200, null=True,default='', verbose_name="昵称") # nickname
    avatar = models.CharField(max_length=250, null=True, default='', verbose_name="头像") # address of the user logo
    site_name = models.CharField(max_length=20, null=True, default='', verbose_name="来源") # site name 
    gender = models.CharField(max_length=1, default='m', null=True, verbose_name="性别")
    access_token = models.CharField(max_length=64, default='', null=True)
    expire_time = models.DateTimeField(null=True)
    refresh_token = models.CharField(max_length=64, default='', null=True)
    cellphone = models.CharField(max_length=11, null=True, blank=True, verbose_name="移动电话")
    
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
    id = models.AutoField(primary_key=True)
    issuer = models.ForeignKey(Poolroom, verbose_name='发起俱乐部')
    issuer_nickname = models.CharField(max_length=20, null=True, blank=True, verbose_name="发起者的昵称")
    starttime = models.DateTimeField(verbose_name='开始时间')
    expiretime = models.DateTimeField(verbose_name='过期时间')
    level = ChoiceTypeField(max_length=12, choices=(
            ('amateur', u'初级球友'),
            ('professional', u'专业高手'),
            ('master', u'职业球手'),
            ('companion', u'陪练(70元/小时)')
        ), verbose_name='发起者水平')
    tabletype = ChoiceTypeField(max_length=10, choices=(
            ('snooker', u'斯诺克 snooker'),
            ('pocket', u'十六彩(美式落袋)'),
            ('nine-ball', u'花式九球'),
            ('any', u'不限')
        ), verbose_name='球台类型')
    rule = models.CharField(max_length=50, verbose_name="比赛方式")
    status = ChoiceTypeField(max_length=7, choices=(
            ('waiting', u'等待匹配'),
            ('matched', u'已经匹配'),
            ('expired', u'已经过期'),
        ), default='waiting', verbose_name='状态', jsonUseValue=False)

    @property
    def is_expired(self):
        return is_expired(self.expiretime)

    @property
    def enroll_count(self):
        return ChallengeApply.objects.filter(challenge=self).count()
    
    @property
    def is_readonly(self):
        rt = self.is_expired or self.status != 'waiting' or self.enroll_count > 0
        return rt
    
    class Meta:
        db_table = 'challenge'
        verbose_name = '约赛'
        verbose_name_plural = '约赛'        
        
    def __unicode__(self):
        return u'%s - %s - %s - %s - %s - %s' %(self.issuer.name, self.starttime, self.get_level_display(), self.get_tabletype_display(), self.rule, self.get_status_display())
   
class ChallengeApply(models.Model):
    id = models.AutoField(primary_key=True)
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
    def create_activity(self, userid, event, keyword, message, recivedtime, reply):
        activity = self.create(userid=userid, eventtype=event, keyword=keyword, message=message, receivedtime=recivedtime, reply=reply)
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
    
    objects = WechatActivityManager()
    
    def __unicode__(self):
        localtz = pytz.timezone(settings.TIME_ZONE)
        return u'[%s] 用户\'%s\' %s发送 %s - %s' %(self.eventtype, self.userid, self.receivedtime.astimezone(localtz), 
                                               self.get_eventtype_display(), self.message)
      
    class Meta:
        db_table = 'wechat_activity'
        verbose_name = '微信用户互动信息'
        verbose_name_plural = '微信用户互动信息'
        
class Event(models.Model):
    id = models.AutoField(primary_key=True)
    year = models.IntegerField(verbose_name='年份')
    month = models.IntegerField(verbose_name='月份')
    title = models.CharField(max_length=30, null=True, blank=True, verbose_name='标题缩写(用于url)')
    
    def __unicode__(self):
        return u'[%s-%s] %s' %(self.year, self.month, self.title)
    
    class Meta:
        db_table = 'event'
        verbose_name = '推广活动'
        verbose_name_plural = '推广活动'
        
class EventCode(models.Model):
    id = models.AutoField(primary_key=True)
    poolroom = models.ForeignKey(Poolroom, verbose_name='台球厅')
    event = models.ForeignKey(Event, verbose_name='推广活动')
    userid = models.CharField(max_length=30, verbose_name='用户id')
    createdtime = models.DateTimeField(verbose_name='创建时间', default=datetime.datetime.now())
    chargecode = models.CharField(max_length=10, verbose_name='消费唯一码', default=generator())
    usedtime = models.DateTimeField(verbose_name='创建时间', blank=True, null=True)
    used = models.BooleanField(verbose_name='使用没有', default=False)
    
    class Meta:
        db_table = 'eventcode'
        verbose_name = '推广活动消费码'
        verbose_name_plural = '推广活动消费码'
