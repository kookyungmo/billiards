# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2013年12月11日

@author: baron
'''

from django.http import HttpResponseRedirect, Http404
from billiards.settings import SOCIALOAUTH_SITES, TEMPLATE_ROOT
from django.contrib.auth.models import User
from django.contrib import auth
from time import mktime, localtime
from datetime import datetime
from billiards.models import PoolroomUser
import copy
from socialoauth import SocialSites
from socialoauth.exception import SocialAPIError
import logging
from urlparse import urlparse
from billiards.commons import isWechatBrowser, forceLogin
from django.shortcuts import render_to_response
from django.http.response import HttpResponse
from django.template.context import RequestContext

# because social site is singleton that has different behavior on different environment
def getSocialSite(request, site_name):
    hostname = u"%s://%s" %("https" if request.is_secure() else "http", request.get_host())
    sites = copy.deepcopy(SOCIALOAUTH_SITES)
    for item in sites:
        origurl = item[3]['redirect_uri']
        item[3]['redirect_uri'] = origurl.replace('$hostname', hostname)
    return sites

def login_3rd(request, site_name):
    socialsites = SocialSites(getSocialSite(request, site_name))
    if site_name in socialsites._sites_name_list:
        _s = socialsites.get_site_object_by_name(site_name)
        if 'returnurl' in request.GET:
            _s.REDIRECT_URI = u"%s?returnurl=%s" %(_s.REDIRECT_URI, request.GET['returnurl'])
        url = _s.authorize_url
        return HttpResponseRedirect(url)
    else:
        raise Http404("Unknown login method '%s'." % site_name)

# not finished yet, to be continued...    
def callback(request, site_name):
    returnurl = '/'
    if 'returnurl' in request.GET:
        returnurl = request.GET.get('returnurl')
    '''
    user store and manage should be replaced by django.contib.auth (TBD)
    '''
    code = request.GET.get('code')
    if not code:
        #error occurred
        return HttpResponseRedirect('/oautherror')
    
    socialsites = SocialSites(getSocialSite(request, site_name))
    _s = socialsites.get_site_object_by_name(site_name)
    
    try:
        _s.get_access_token(code)
    except SocialAPIError as e:
        print e.site_name   # the site_name which has error occurred
        print e.url         # the url requested
        print e.error_msg   # the error log returned from the site
        raise
    
    if _s.site_name != 'wechat':
        username = _s.uid[0:29]
        password = _s.site_name + _s.uid[30:]
    else:
        username = _s.uid
        password = _s.site_name + _s.uid
    
    user = auth.authenticate(username=username, password=password)
   
    if user is None:
        user = User.objects.create_user(username=username, password=password)
        user.site_name = _s.site_name
        user.save()
        user = auth.authenticate(username=username, password=(password))        
    
    if user.is_active == 0:
        return HttpResponseRedirect(returnurl)

    if _s.site_name != 'wechat':
        user.nickname = _s.name
    else:
        user.nickname = _s.name.encode('unicode_escape')
#     user.gender = (lambda x: 'm' if x else 'f')(_s.gender)
    user.avatar = _s.avatar
    user.access_token = _s.access_token
    user.expire_time = datetime.fromtimestamp(mktime(localtime()) + _s.expires_in)
    user.refresh_token = _s.refresh_token
    user.save()
    
    poolrooms = list(PoolroomUser.objects.filter(user=user))
    if len(poolrooms) > 0:
        user.is_club_owner = True
        user.poolroom = poolrooms[0].poolroom
    else:
        user.poolroom = None
    auth.login(request, user)
    
    return HttpResponseRedirect(returnurl)

logger = logging.getLogger("login")

def logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
       
    return HttpResponseRedirect('/')
    
    
def oautherror(request):
    print "OAuth Error"
    return HttpResponseRedirect('/')    #should have some ERROR info here, TBD
    
def login_3rd_page(request):
    try:
        fromurl = request.GET['from']
        fromurl = urlparse(fromurl).path
        if not request.user.is_authenticated():
            if isWechatBrowser(request.META['HTTP_USER_AGENT']):
                return forceLogin(request, 'wechat', fromurl)
            return render_to_response(TEMPLATE_ROOT + 'escort/waplogin.html', {'from': fromurl}, context_instance=RequestContext(request))
    except KeyError:
        response = HttpResponse("invalid request")
        response.status_code = 400
        return response
    return HttpResponseRedirect(fromurl)
    