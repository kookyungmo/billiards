# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2013年10月31日

@author: kane
'''
from django import template
from django.core import serializers
from django.db.models.query import QuerySet, ValuesQuerySet
from billiards.models import match_fields, poolroom_fields, PoolroomEquipment

def tojson(data, fields = None):
    json_serializer = serializers.get_serializer("json")()
    newdata = data
    if not isinstance(newdata, (QuerySet, ValuesQuerySet)):
        newdata = [data]
    jsonstring = json_serializer.serialize(newdata, fields=fields,
                                               ensure_ascii=False, use_natural_keys=True)
    return jsonstring

def poolroomtojson(data):
    return tojson(data, poolroom_fields)

def matchtojson(data):
    return tojson(data, match_fields)

def equipmentname(equipment):
    if isinstance(equipment, (PoolroomEquipment)):
        return equipment.get_tabletype_display()
    raise Exception()

register = template.Library()
register.filter('matchtojson', matchtojson)
register.filter('poolroomtojson', poolroomtojson)
register.filter('tojson', tojson)
register.filter('equipmentname', equipmentname)