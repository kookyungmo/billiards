# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2013年10月31日

@author: kane
'''
from django import template
from django.core import serializers
from django.db.models.query import QuerySet, ValuesQuerySet

def tojson(data, fields = None):
    json_serializer = serializers.get_serializer("json")()
    newdata = data
    if not isinstance(newdata, (QuerySet, ValuesQuerySet)):
        newdata = [data]
    jsonstring = json_serializer.serialize(newdata, fields=fields,
                                               ensure_ascii=False, use_natural_keys=True)
    return jsonstring

def matchtojson(data):
    return tojson(data, ('id', 'poolroom', 'bonus', 'bonusdetail', 'rule', 'starttime', 'description'))

register = template.Library()
register.filter('matchtojson', matchtojson)
register.filter('tojson', tojson)