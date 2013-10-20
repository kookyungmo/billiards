# -*- coding: utf-8 -*-
# encoding: utf-8
'''

@author: kane
'''

from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world. You're at the poll index.")