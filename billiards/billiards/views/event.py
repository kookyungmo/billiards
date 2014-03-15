# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2014年3月14日

@author: kane
'''
from django.shortcuts import render_to_response
from billiards.settings import TEMPLATE_ROOT
from django.template.context import RequestContext

def detail(request, year, month, title=None):
    return render_to_response(TEMPLATE_ROOT + 'event/nextstepu.html', {},
        context_instance=RequestContext(request))