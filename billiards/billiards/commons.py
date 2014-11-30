# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2014年7月12日

@author: kane
'''
from urllib import urlencode
from urlparse import urlsplit, parse_qs, urlunsplit
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.db.models.query import QuerySet, ValuesQuerySet
from StringIO import StringIO
from django.core.serializers.json import Serializer
from django.utils.encoding import is_protected_type
from datetime import datetime
from bitfield.models import BitField
from billiards import settings
from billiards.bcms import mail

KEY_PREFIX = 'location_%s_%s'

def set_query_parameter(url, param_name, param_value):
    """Given a URL, set or replace a query parameter and return the
    modified URL.

    >>> set_query_parameter('http://example.com?foo=bar&biz=baz', 'foo', 'stuff')
    'http://example.com?foo=stuff&biz=baz'

    """
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)

    query_params[param_name] = [param_value]
    new_query_string = urlencode(query_params, doseq=True)

    return urlunsplit((scheme, netloc, path, new_query_string, fragment))

def forceLogin(request, sitename):
    url = set_query_parameter(reverse('login_3rd', args=(sitename,)), 'returnurl', request.build_absolute_uri(request.get_full_path()))
    return HttpResponseRedirect(url)

def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)
    
def tojson(data, fields = None):
    json_serializer = DisplayNameJsonSerializer()
    return tojson2(data, json_serializer, fields)

def tojson2(data, serialize, fields = None):
    newdata = data
    if not isinstance(newdata, (QuerySet, ValuesQuerySet)):
        newdata = [data]
    stream = StringIO()
    serialize.serialize(newdata, fields=fields, stream=stream,
            ensure_ascii=False, use_natural_keys=True)
    return stream.getvalue()

class DisplayNameJsonSerializer(Serializer): 

    def handle_field(self, obj, field): 
        value = field._get_val_from_obj(obj) 

        #If the object has a get_field_display() method, use it. 
        display_method = "get_%s_display" % field.name 
        if  hasattr(field, 'json_use_value') and getattr(field, 'json_use_value')() == True:
            if isinstance(field, BitField):
                self._current[field.name] = int(value)
            else:
                self._current[field.name] = value
        elif hasattr(obj, display_method): 
            self._current[field.name] = getattr(obj, display_method)() 
        # Protected types (i.e., primitives like None, numbers, dates, 
        # and Decimals) are passed through as is. All other values are 
        # converted to string first. 
        elif is_protected_type(value): 
            self._current[field.name] = value 
        else: 
            self._current[field.name] = field.value_to_string(obj) 
    
class NoObjectJSONSerializer(DisplayNameJsonSerializer):
    def get_dump_object(self, obj):
        return self._current or {}
    
def decodeunicode(str1):
    try:
        return str1.decode('unicode_escape')
    except UnicodeEncodeError:
        return str1
    
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    
def notification(subject, body):
    notification_mail(subject, body)
def notification_mail(subject, body):
    mail(settings.NOTIFICATION_EMAIL, subject, body)