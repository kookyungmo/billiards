# -*- coding: utf-8 -*-
# encoding: utf-8
'''

@author: kane
'''
from billiards import settings
from billiards.settings import STATIC_URL, SITE_LOGO_URL
from datetime import datetime

BUILDID = 20131210
REV = '2013.12.15.abcdef'
SCSSHASH = 'abcdefg'
APPJSHASH = 'abcdefg'
ESCORTJSHASH = 'abcdefg'
def siteconf(request):
    """
    Adds ibilliards global context variables to the context.

    """
    return {
            'buildid': datetime.now().strftime("%y%m%d%H") if settings.DEBUG else BUILDID,
            'scsshash': SCSSHASH,
            'appjshash': APPJSHASH,
            'escortjshash': ESCORTJSHASH,
            'rev': REV,
            'STATIC_URL': STATIC_URL,
            'SITE_LOGO_URL': SITE_LOGO_URL,
            'FOUNDATION_VER': '5.3.3',
            'JS_CDN_PREFIX': '//cdnjscn.b0.upaiyun.com',
            'AWESOME_FONT': '4.1.0',
            'UUID_SAMPLE': '12345678-1234-1234-1234-123456789012',
            'pagetitle': u'我为台球狂',
    }