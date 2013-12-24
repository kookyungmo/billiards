# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2013年10月21日

@author: kane
'''
from billiards.models import Poolroom, Match, PoolroomEquipment
from django.contrib import admin
from bitfield import BitField
from bitfield.forms import BitFieldCheckboxSelectMultiple
from bitfield.admin import BitFieldListFilter
from billiards.location_convertor import gcj2bd

class ModelWithFlagsAdmin(admin.ModelAdmin):
    formfield_overrides = {
        BitField: {'widget': BitFieldCheckboxSelectMultiple},
    }

class MatchAdmin(ModelWithFlagsAdmin):
    list_filter = (
            ('flags', BitFieldListFilter),
            )

class PoolroomAdmin(ModelWithFlagsAdmin):
    list_filter = (
            ('flags', BitFieldListFilter),
            )
    def save_model(self, request, obj, form, change):
        # custom stuff here
        if (obj.lat_baidu == 0 or obj.lng_baidu == 0) and (obj.lat != 0 and obj.lng != 0):
            baiduLoc = gcj2bd(float(obj.lat), float(obj.lng))
            obj.lat_baidu = baiduLoc[0]
            obj.lng_baidu = baiduLoc[1]
        obj.save()

admin.site.register(Poolroom, PoolroomAdmin)
admin.site.register(PoolroomEquipment)
admin.site.register(Match, MatchAdmin)