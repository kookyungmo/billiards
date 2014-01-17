# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2013年12月11日

@author: baron
'''

from django.http import HttpResponseRedirect, Http404
from billiards.settings import SOCIALOAUTH_SITES
from billiards.support.socialoauth import SocialSites, SocialAPIError
from django.contrib.auth.models import User
from django.contrib import auth
from time import mktime, localtime
from datetime import datetime
from billiards.models import PoolroomUser
import copy


def login_3rd(request, site_name):
    hostname = u"%s://%s" %("https" if request.is_secure() else "http", request.get_host())
    sites = copy.deepcopy(SOCIALOAUTH_SITES)
    for item in sites:
        if item[0] == site_name:
            origurl = item[3]['redirect_uri']
            item[3]['redirect_uri'] = origurl.replace('$hostname', hostname)
            if 'returnurl' in request.GET:
                baseurl = item[3]['redirect_uri']
                item[3]['redirect_uri'] = u"%s?returnurl=%s" %(baseurl, request.GET['returnurl'])
            break
    socialsites = SocialSites(sites)
    if site_name in socialsites._sites_name_list:
        _s = socialsites.get_site_object_by_name(site_name)
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
    
    socialsites = SocialSites(SOCIALOAUTH_SITES)
    _s = socialsites.get_site_object_by_name(site_name)
    
    try:
        _s.get_access_token(code)
    except SocialAPIError as e:
        print e.site_name   # the site_name which has error occurred
        print e.url         # the url requested
        print e.error_msg   # the error log returned from the site
        raise
    
    username = _s.uid[0:29]
    password = _s.site_name + _s.uid[30:]
    
    user = auth.authenticate(username=username, password=password)
   
    if user is None:
        user = User.objects.create_user(username=username, password=password)
        user.save()
        user = auth.authenticate(username=_s.uid[0:29], password=(_s.site_name+_s.uid[30:]))        
    
    if user.is_active == 0:
        return HttpResponseRedirect(returnurl)

    user.nickname = _s.name
    user.gender = (lambda x: 'm' if x else 'f')(_s.gender)
    user.avatar = _s.avatar
    user.site_name = _s.site_name
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
    

def logout(request):

    auth.logout(request)
    return HttpResponseRedirect('/')
    
    
def oautherror(request):
    print "OAuth Error"
    return HttpResponseRedirect('/')    #should have some ERROR info here, TBD
    
    
    