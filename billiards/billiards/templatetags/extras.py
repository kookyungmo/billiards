# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2013年10月31日

@author: kane
'''
from django import template
from billiards.models import match_fields, poolroom_fields, PoolroomEquipment,\
    PoolroomImage, getThumbnailPath
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

def thumbnail(imagepath, width):
    return thumbnail2(imagepath.name, width)

def thumbnail2(imagepath, length, prefix = 'w'):
    return getThumbnailPath(imagepath.name, length, prefix)

def classname(obj):
    classname = obj.__class__.__name__
    return classname

register = template.Library()
register.filter('matchtojson', matchtojson)
register.filter('poolroomtojson', poolroomtojson)
register.filter('tojson', tojson)
register.filter('equipmentname', equipmentname)
register.filter('matchtojsonwithenroll', matchtojsonwithenroll)
register.filter('thumbnail', thumbnail)
register.filter('classname', classname)

@register.filter
def get_range( value ):
    """
    Filter - returns a list containing range made from given value
    Usage (in template):

    <ul>{% for i in 3|get_range %}
      <li>{{ i }}. Do something</li>
    {% endfor %}</ul>

    Results with the HTML:
    <ul>
      <li>0. Do something</li>
      <li>1. Do something</li>
      <li>2. Do something</li>
    </ul>

    Instead of 3 one may use the variable set in the views
    """
    return range( value )

@register.filter
def decodeunicode(str1):
    try:
        return str1.decode('unicode_escape')
    except UnicodeEncodeError:
        return str1
    
@register.filter    
def subtract(value, arg):
    try:
        return value - long(arg)
    except Exception:
        return value
    
"""
jQuery templates use constructs like:

    {{if condition}} print something{{/if}}

Or like:

    {% if condition %} print {%=object.something %}{% endif %}

This, of course, completely screws up Django templates,
because Django thinks {{ and }} mean something.

Wrap {% verbatim %} and {% endverbatim %} around those
blocks of jQuery templates and this will try its best
to output the contents with no changes.
"""
class VerbatimNode(template.Node):

    def __init__(self, text):
        self.text = text

    def render(self, context):
        return self.text

@register.tag
def verbatim(parser, token):
    text = []
    while 1:
        token = parser.tokens.pop(0)
        if token.contents == 'endverbatim':
            break
        if token.token_type == template.TOKEN_VAR:
            text.append('{{ ')
        elif token.token_type == template.TOKEN_BLOCK:
            text.append('{%')
        text.append(token.contents)
        if token.token_type == template.TOKEN_VAR:
            text.append(' }}')
        elif token.token_type == template.TOKEN_BLOCK:
            if not text[-1].startswith('='):
                text[-1:-1] = [' ']
            text.append(' %}')
    return VerbatimNode(''.join(text))