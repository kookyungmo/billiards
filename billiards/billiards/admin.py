# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2013年10月21日

@author: kane
'''
from billiards.models import Poolroom, Match
from django.contrib import admin
from bitfield import BitField
from bitfield.forms import BitFieldCheckboxSelectMultiple
from bitfield.admin import BitFieldListFilter

class PoolroomAdmin(admin.ModelAdmin):
    formfield_overrides = {
            BitField: {'widget': BitFieldCheckboxSelectMultiple},
    }

    list_filter = (
            ('flags', BitFieldListFilter),
            )

admin.site.register(Poolroom, PoolroomAdmin)
admin.site.register(Match)