# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2014年1月5日

@author: kane
'''
from django.shortcuts import render_to_response, get_object_or_404
from billiards.settings import TEMPLATE_ROOT
from django.template.context import RequestContext
from billiards.models import Coupon
from billiards.views.match import getMatch
from django.http import Http404
from billiards.views.poolroom import getPoolroom
from billiards.views.challenge import getChallenge
'''
Base on a responsive web page template that works well on IE7 and IE8.
It won't work on IE6, but it also gives very simple text for information.
http://www.prowebdesign.ro/simple-responsive-template-free/
'''
def unsupportedbrowser(request):
    return render_to_response(TEMPLATE_ROOT + 'unsupportedbrowser.html',
                              {},
                              context_instance=RequestContext(request))
    
def coupon(request, couponid):
    coupon = get_object_or_404(Coupon, pk=couponid)
    return render_to_response(TEMPLATE_ROOT + 'coupon_tracker.html',
                              {'coupon': coupon},
                              context_instance=RequestContext(request))
    
def wechatsharehelp(request):
    return render_to_response(TEMPLATE_ROOT + 'wechatsharehelp.html',
                              {'text': request.GET['text']},
                              context_instance=RequestContext(request))
    
def survey_redbull(request):
    return render_to_response(TEMPLATE_ROOT + 'survey_redbull.html',
                              {}, context_instance=RequestContext(request))
    
def pkmap(request, mtype = None, tid = None):
    if mtype == None:
        mtype = request.GET.get('type')
        tid = request.GET.get('id')
    try:
        targetObj = None
        if mtype == 'match':
            targetObj = getMatch(tid)
            name = targetObj.title
        elif mtype == 'poolroom':
            targetObj = getPoolroom(tid)
            name = targetObj.name
        elif mtype == 'challenge':
            targetObj = getChallenge(tid)
    except Http404:
        pass
    return render_to_response(TEMPLATE_ROOT + 'pkmap.html',
                              {'target': targetObj, 'name': name}, context_instance=RequestContext(request))