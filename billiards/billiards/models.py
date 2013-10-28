# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2013年10月21日

@author: kane
'''

from django.db import models
from django.utils.timezone import localtime

class Poolroom(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200,null=False,verbose_name='名字')
    address = models.TextField(null=True,verbose_name='地址')
    tel = models.CharField(max_length=20,null=True,verbose_name='电话')
    lat = models.DecimalField(max_digits=11,decimal_places=7,null=True,verbose_name='纬度')
    lng = models.DecimalField(max_digits=11,decimal_places=7,null=True,verbose_name='经度')

    class Meta:
        db_table = 'poolroom'
        verbose_name = '台球厅'
        verbose_name_plural = '台球厅'

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return {'id': self.id, 'name': self.name, 'lat': self.lat, 'lng': self.lng}

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
