# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2013年10月21日

@author: kane
'''

from django.db import models
from django.utils.timezone import localtime
from bitfield import BitField
from django.db.models.fields import Field

class Poolroom(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200,null=False,verbose_name='名字')
    address = models.TextField(null=True,verbose_name='地址')
    tel = models.CharField(max_length=20,null=True,verbose_name='电话')
    lat = models.DecimalField(max_digits=11,decimal_places=7,null=True,verbose_name='纬度')
    lng = models.DecimalField(max_digits=11,decimal_places=7,null=True,verbose_name='经度')
    #TODO try composite bit field
    flags = BitField(flags=(
            ('wifi', 'Wifi'),
            ('wifi_free', '免费Wifi'),
            ('parking', '停车位'),
            ('parking_free', ' 免费停车位'),
            ('cafeteria', '餐厅'),
            ('subway', ' 地铁周边'),
        ), verbose_name='特色属性', default=0)

    class Meta:
        db_table = 'poolroom'
        verbose_name = '台球厅'
        verbose_name_plural = '台球厅'

    def __unicode__(self):
        return self.name

    def natural_key(self):
        flag_dict = {}
        for f in self.flags:
            flag_dict[f[0]] = f[1]
        return {'id': self.id, 'name': self.name, 'lat': self.lat, 'lng': self.lng,
                'address': self.address, 'flags': flag_dict}

class Match(models.Model):
    id = models.AutoField(primary_key=True)
    poolroom = models.ForeignKey(Poolroom, verbose_name='比赛组织者')
    bonus = models.FloatField(null=False,verbose_name='最高奖金(元)')
    description = models.TextField(null=True,verbose_name='比赛详情')
    starttime = models.DateTimeField(verbose_name='比赛开始时间')

    class Meta:
        db_table = 'match'
        verbose_name = '比赛'
        verbose_name_plural = '比赛'

    def __unicode__(self):
        return '[' + localtime(self.starttime).strftime("%Y-%m-%d %H:%M:%S") + '] ' + self.poolroom.name
