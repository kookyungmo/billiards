# -*- coding: utf-8 -*-
# encoding: utf-8
'''
@author: kane
A utility tool to show the ip address of host running this tool.
'''
from django.core.management.base import NoArgsCommand
import requests
from django.utils.timezone import localtime, now
from billiards.management.commands.msgprocessor import TIME_FORMAT
import re

class Command(NoArgsCommand):
    help = 'Show host ip address'
    
    def handle(self, *args, **options):
        r = requests.get('http://www.iplocation.net/')
        if r.status_code == requests.codes.ok:
            ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', r.text)
            print '[%s]IP address is %s.' %(localtime(now()).strftime(TIME_FORMAT), ip[0])
        else:
            print '[%s]Failed to request ip from iplocation.net.' %(localtime(now()).strftime(TIME_FORMAT))