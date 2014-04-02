# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2014年3月14日

@author: kane
'''
from django.shortcuts import render_to_response, get_object_or_404
from billiards.settings import TEMPLATE_ROOT
from django.template.context import RequestContext
from billiards.models import Event

def detail(request, year, month, title=None):
    get_object_or_404(Event, year=year, month=int(month))
    return render_to_response(TEMPLATE_ROOT + 'event/nextstepu_qiang.html', {},
        context_instance=RequestContext(request))
