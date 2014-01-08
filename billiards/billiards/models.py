# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2013年10月21日

@author: kane
'''

from django.db import models
from django.utils.timezone import localtime
from bitfield import BitField
from django.utils.encoding import force_unicode
from django.contrib.auth.models import User
from billiards.storage import ImageStorage
from billiards.settings import UPLOAD_TO

def toDict(bitfield):
    flag_dict = {}
    for f in bitfield:
        flag_dict[f[0]] = f[1]
    return flag_dict

poolroom_fields = ('id', 'name', 'address', 'tel', 'lat_baidu', 'lng_baidu', 'flags', 'businesshours', 'size', 'rating')
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
        return {'id': self.id, 'name': self.name, 'lat': self.lat_baidu, 'lng': self.lng_baidu,
                'businesshours': self.businesshours, 'size': self.size,
                'address': self.address, 'flags': toDict(self.flags), 'rating': self.rating}

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
        return force_unicode(dict(self.flatchoices).get(value, value), strings_only=True)
    
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

match_fields = ('id', 'poolroom', 'bonus', 'rechargeablecard', 'otherprize', 'bonusdetail', 'rule', 'starttime', 'description')
class Match(models.Model):
    id = models.AutoField(primary_key=True)
    poolroom = models.ForeignKey(Poolroom, verbose_name='比赛组织者')
    bonus = models.FloatField(null=False,verbose_name='最高现金奖金金额(元)')
    rechargeablecard = models.FloatField(null=False, verbose_name='最高充值卡奖金金额(元)')
    otherprize = models.CharField(max_length=100,null=True,blank=True,verbose_name='最高其它类别奖励')
    bonusdetail = models.TextField(null=False,verbose_name='奖金细则')
    rule = models.TextField(null=False,verbose_name='比赛规则')
    description = models.TextField(null=True,verbose_name='比赛详情')
    starttime = models.DateTimeField(verbose_name='比赛开始时间')
    enrollfee = models.CharField(max_length=100,null=True,verbose_name='报名费')
    enrollfocal = models.CharField(max_length=100,null=True,verbose_name='报名联系人')
    flags = BitField(flags=(
            ('groupon', u'支持团购'),
            ('coupon', u'支持用券'),
        ), verbose_name='特色属性')

    class Meta:
        db_table = 'match'
        verbose_name = '比赛'
        verbose_name_plural = '比赛'

    def __unicode__(self):
        return '[' + localtime(self.starttime).strftime("%Y-%m-%d %H:%M:%S") + '] ' + self.poolroom.name

    def natural_key(self):
        return {'id': self.id, 'poolroom': self.poolroom.natural_key(), 'bonus': self.bonus,
                'rechargeablecard': self.rechargeablecard, 'description': self.description,
                'otherprize': self.otherprize,
                'bonusdetail': self.bonusdetail, 'rule': self.rule,
                'starttime': self.starttime, 'enrollfee': self.enrollfee,
                'enrollfocal': self.enrollfocal, 'flags': toDict(self.flags)}

    def save(self):
        super(Match, self).save()
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

class ProfileBase(type):
    def __new__(cls, name, bases, attrs):
        module = attrs.pop('__module__')
        parents = [b for b in bases if isinstance(b, ProfileBase)]
        if parents:
            fields = []
            for obj_name, obj in attrs.items():
                if isinstance(obj, models.Field): fields.append(obj_name)
                User.add_to_class(obj_name, obj)
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
            ('submitted', u'已提交'),
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
    def verbose_username(self):
        return "%s <br/>Email: %s<br/>Tel: %s" % ((self.user.nickname if self.user.nickname is not None and self.user.nickname != "" else self.user.username), self.user.email, self.user.cellphone)
    verbose_username.short_description = u'用户详细信息'
    verbose_username.allow_tags = True
        
        
UPLOAD_TO = UPLOAD_TO + 'poolroom/'
class Images(models.Model):
    user = models.ForeignKey(User, verbose_name=u"当前用户", related_name="userimages")
    picture = models.ImageField(verbose_name=u'图片', max_length=250,
                                     upload_to=UPLOAD_TO,
                                     storage=ImageStorage(),
                                     null=True, blank=True)

    def __unicode__(self):
        return u"%s" % self.user

    class Meta:
        verbose_name = u'图片文件夹'
        verbose_name_plural = verbose_name   

    def delete(self, using=None):
        try:
            self.picture.storage.delete(self.picture.name)
        except Exception:
            pass
        super(Images, self).delete(using=using)
