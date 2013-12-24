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
from django.contrib.auth.admin import UserAdmin

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
        ), verbose_name='特色属性')
    businesshours = models.CharField(max_length=60,null=True,verbose_name='营业时间')
    size = models.IntegerField(max_length=8,null=True,verbose_name='球馆面积(平米)')
    rating = models.IntegerField(max_length=2,null=True,verbose_name='球房总评分')

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

class TableTypeField(models.CharField):
    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return force_unicode(dict(self.flatchoices).get(value, value), strings_only=True)

class PoolroomEquipment(models.Model):
    id = models.AutoField(primary_key=True)
    poolroom = models.ForeignKey(Poolroom, verbose_name='台球厅')
    tabletype = TableTypeField(max_length=10, choices=(
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
            UserAdmin.fieldsets = list(UserAdmin.fieldsets)
            UserAdmin.fieldsets.append((name, {'fields': fields}))
        return super(ProfileBase, cls).__new__(cls, name, bases, attrs)
        
class ProfileObject(object):
    __metaclass__ = ProfileBase

class Profile(ProfileObject):
    nickname = models.TextField(max_length=200, null=True,default='', verbose_name="昵称") # nickname
    avatar = models.CharField(max_length=250, null=True, default='', verbose_name="头像") # address of the user logo
    site_name = models.CharField(max_length=20, null=True, default='', verbose_name="来源") # site name 
    gender = models.CharField(max_length=1, default='m', null=True, verbose_name="性别")
    

      
