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
from django.core.exceptions import MultipleObjectsReturned

def detail(request, year, month, title=None):
    try:
        event = get_object_or_404(Event, year=year, month=int(month))
    except MultipleObjectsReturned:
        event = get_object_or_404(Event, year=year, month=int(month), title=title)
    return render_to_response(TEMPLATE_ROOT + 'event/%s' %(event.pagename), {},
        context_instance=RequestContext(request))