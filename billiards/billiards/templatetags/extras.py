# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2013年10月31日

@author: kane
'''
from django import template
from django.core import serializers
from django.db.models.query import QuerySet

def tojson(data):
    json_serializer = serializers.get_serializer("json")()
    newdata = data
    if not isinstance(newdata, (QuerySet)):
        newdata = [data]
    jsonstring = json_serializer.serialize(newdata, fields=('id', 'poolroom', 'bonus', 'starttime', 'description'),
                                               ensure_ascii=False, use_natural_keys=True)
    return jsonstring

register = template.Library()
register.filter('tojson', tojson)