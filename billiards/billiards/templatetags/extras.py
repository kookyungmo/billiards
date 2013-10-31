# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2013年10月31日

@author: kane
'''
from django import template
from django.core import serializers
from django.utils.html import escape

def tojson(data):
    json_serializer = serializers.get_serializer("json")()
    jsonstring = json_serializer.serialize([data], fields=('id', 'poolroom', 'bonus', 'starttime', 'description'),
                                               ensure_ascii=False, use_natural_keys=True)
    return escape(jsonstring)

register = template.Library()
register.filter('tojson', tojson)