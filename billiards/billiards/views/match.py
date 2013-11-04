# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2013年10月22日

@author: kane
'''
from django.shortcuts import render_to_response, get_object_or_404
from billiards.models import Match
import datetime
from dateutil.relativedelta import relativedelta
from django.core import serializers
from django.http import HttpResponse

templatepath = 'foundation4/'
def index(request, view = None):
    starttime = datetime.datetime.today()
    try:
        if request.GET.get('starttime') is not None:
            starttime = datetime.datetime.utcfromtimestamp(float(request.GET.get('starttime'))/1000)
    except Exception:
        pass
    endtime = starttime + relativedelta(weeks=2)
    try:
        if request.GET.get('endtime') is not None:
            endtime = datetime.datetime.utcfromtimestamp(float(request.GET.get('endtime'))/1000)
    except Exception:
        pass

    matches = Match.objects.filter(starttime__gte=starttime.strftime("%Y-%m-%d")) \
        .exclude(starttime__gt=endtime.strftime("%Y-%m-%d")).order_by('starttime')

    if request.GET.get('f') == 'json':
        json_serializer = serializers.get_serializer("json")()
        response = HttpResponse()
        json_serializer.serialize(matches, fields=('id', 'poolroom', 'bonus', 'starttime'), ensure_ascii=False, stream=response, indent=2, use_natural_keys=True)
        return response
    if view == 'map':
        page = 'match_map.html'
    else:
        page = 'match_list.html'

    return render_to_response(templatepath + page, {'matches': matches, 'starttime': starttime, 'enddate': endtime})

def detail(request, matchid):
    match = get_object_or_404(Match, pk=matchid)

    if request.GET.get('f') == 'json':
        json_serializer = serializers.get_serializer("json")()
        response = HttpResponse()
        json_serializer.serialize([match], fields=('id', 'poolroom', 'bonus', 'starttime', 'description'), ensure_ascii=False, stream=response, indent=2, use_natural_keys=True)
        return response

    return render_to_response(templatepath + 'match_detail.html', {'match': match})