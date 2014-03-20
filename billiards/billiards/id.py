# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2014年3月20日

@author: kane
'''
import string
import random
def generator(size=7, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))