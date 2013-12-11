# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2013年12月11日

@author: baron
'''

from django.http import HttpResponseRedirect, Http404
from billiards.settings import SOCIALOAUTH_SITES
from socialoauth import SocialSites


def login(request, site_name):
    socialsites = SocialSites(SOCIALOAUTH_SITES)
    
    if site_name in socialsites._sites_name_list:
        _s = socialsites.get_site_object_by_name(site_name)
        url = _s.authorize_url
        return HttpResponseRedirect(url)
    else:
        raise Http404("Unknown login method '%s'." % site_name)
    

    