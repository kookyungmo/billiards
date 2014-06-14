# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2014年6月14日

@author: kane
'''
from billiards.settings import TEMPLATE_ROOT
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from billiards.models import Goods
from django.http import Http404

def membership(request):
    goods = Goods.objects.all()[:1]
    if len(goods) == 0:
        raise Http404
    goods = goods[0]
    return render_to_response(TEMPLATE_ROOT + '/trade/base.html',
                              {'sku': goods.sku}, context_instance=RequestContext(request))