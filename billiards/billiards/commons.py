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