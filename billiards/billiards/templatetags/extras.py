# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2013年10月31日

@author: kane
'''
from django import template
from billiards.models import match_fields, poolroom_fields, PoolroomEquipment
from billiards.views import match
from billiards.views.match import tojson

def poolroomtojson(data):
    return tojson(data, poolroom_fields)

def matchtojson(data):
    return tojson(data, match_fields)

def equipmentname(equipment):
    if isinstance(equipment, (PoolroomEquipment)):
        return equipment.get_tabletype_display()
    raise Exception()

def matchtojsonwithenroll(matches, user):
    jsonstr = matchtojson(matches)
    if user.is_authenticated():
        return match.updateMatchJsonStrEnrollInfo(jsonstr, user, matches)
    else:
        return jsonstr

register = template.Library()
register.filter('matchtojson', matchtojson)
register.filter('poolroomtojson', poolroomtojson)
register.filter('tojson', tojson)
register.filter('equipmentname', equipmentname)
register.filter('matchtojsonwithenroll', matchtojsonwithenroll)