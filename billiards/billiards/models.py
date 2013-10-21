# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2013年10月21日

@author: kane
'''

from django.db import models

class Poolroom(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200,null=False,verbose_name='名字')
    address = models.TextField(null=True,verbose_name='地址')
    tel = models.CharField(max_length=20,null=True,verbose_name='电话')
    lat = models.DecimalField(max_digits=10,decimal_places=6,null=True,verbose_name='纬度')
    lng = models.DecimalField(max_digits=10,decimal_places=6,null=True,verbose_name='经度')

    class Meta:
        db_table = 'poolroom'
        verbose_name = '台球厅'
        verbose_name_plural = '台球厅'

    def __unicode__(self):
        return self.name
