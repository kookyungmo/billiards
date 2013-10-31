# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2013年10月22日

@author: kane
'''
from django.shortcuts import render_to_response
from billiards.models import Match
import datetime
from dateutil.relativedelta import relativedelta
from django.core import serializers
from django.http import HttpResponse
import json
from django import template

templatepath = 'foundation4/'
def index(request, view = None):
    date_after_week = datetime.datetime.today() + relativedelta(weeks=2)
    matches = Match.objects.filter(starttime__gte=datetime.datetime.now().strftime("%Y-%m-%d %H:%m")) \
        .exclude(starttime__gte=date_after_week.strftime("%Y-%m-%d %H:%m")).order_by('starttime')

    if request.GET.get('f') == 'json':
        json_serializer = serializers.get_serializer("json")()
        response = HttpResponse()
        json_serializer.serialize(matches, fields=('id', 'poolroom', 'bonus', 'starttime'), ensure_ascii=False, stream=response, indent=2, use_natural_keys=True)
        return response
    if view == 'map':
        page = 'match_map.html'
    else:
        page = 'match_list.html'

    return render_to_response(templatepath + page, {'matches': matches})

def detail(request, matchid):
    match = Match.objects.get(pk=matchid)

    if request.GET.get('f') == 'json':
        json_serializer = serializers.get_serializer("json")()
        response = HttpResponse()
        json_serializer.serialize([match], fields=('id', 'poolroom', 'bonus', 'starttime', 'description'), ensure_ascii=False, stream=response, indent=2, use_natural_keys=True)
        return response

    return render_to_response(templatepath + 'match_detail.html', {'match': match})