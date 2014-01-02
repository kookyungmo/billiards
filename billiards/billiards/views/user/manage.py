# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2014年1月1日

@author: kane
'''
from django.http import HttpResponse

def completeInfo(request):
    user = request.user
    if user.is_authenticated():
        user.cellphone = request.GET.get('tel')
        user.email = request.GET.get('email')
        user.save()
    return HttpResponse