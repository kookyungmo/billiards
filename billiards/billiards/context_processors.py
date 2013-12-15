'''

@author: kane
'''
from billiards import settings
import time

BUILDID = 20131210
REV = '2013.12.15.abcdef'
def siteconf(request):
    """
    Adds ibilliards global context variables to the context.

    """
    return {
            'buildid': int(time.time()) if settings.DEBUG else BUILDID,
            'rev': REV
    }