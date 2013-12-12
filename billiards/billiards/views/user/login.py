# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2013年12月11日

@author: baron
'''

from django.http import HttpResponseRedirect, Http404, HttpResponse
from billiards.settings import SOCIALOAUTH_SITES
from billiards.support.socialoauth import SocialSites, SocialAPIError
from billiards.support.helper import Session, UserStorage



def login(request, site_name):
    socialsites = SocialSites(SOCIALOAUTH_SITES)
    if site_name in socialsites._sites_name_list:
        _s = socialsites.get_site_object_by_name(site_name)
        url = _s.authorize_url
        return HttpResponseRedirect(url)
    else:
        raise Http404("Unknown login method '%s'." % site_name)

# not finished yet, to be continued...    
def callback(request, site_name):
    
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
    
    storage = UserStorage()
    UID = storage.get_uid(_s.site_name, _s.uid)
    if not UID:
        # bind a UID in local for the user login for the first time
        UID = storage.bind_new_user(_s.site_name, _s.uid)
        
    storage.set_user(
        UID,
        site_name = _s.site_name,
        uid = _s.uid,
        name = _s.name,
        avatar = _s.avatar
    )
    
    session_id = request.COOKIES.get('session_id')
    if not session_id:
        session_id = Session.make_session_id(UID)
    session = Session()
    session.set(session_id, uid = UID)
    HttpResponse.set_cookie('session_id', session_id)
    
    return HttpResponseRedirect('/')


def logout(request):
    session_id = request.COOKIES.get('session_id')
    if not session_id:
        return HttpResponseRedirect('/')

    session = Session()
    data = session.get(session_id)
    session.rem(session_id)
    uid = data.get('uid', None)
    if uid:
        # reset session_id
        Session.refresh_session_id(uid)

    HttpResponse.set_cookie('session_id', '')
    return HttpResponseRedirect('/')
    
    
def oautherror():
    print "OAuth Error"
    return HttpResponseRedirect('/')    #should have some ERROR info here, TBD
    
    

    