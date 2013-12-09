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
from billiards.settings import STATIC_URL
from django.template.context import RequestContext
from django.db.models.aggregates import Max
from django.utils import simplejson

templatepath = 'foundation4/'
def index(request, view = None):
    starttime = datetime.datetime.today()
    try:
        if request.GET.get('starttime') is not None:
            starttime = datetime.datetime.utcfromtimestamp(float(request.GET.get('starttime'))/1000)
    except Exception:
        pass
    endtime = starttime + relativedelta(days=1)
    try:
        if request.GET.get('endtime') is not None:
            endtime = datetime.datetime.utcfromtimestamp(float(request.GET.get('endtime'))/1000)
    except Exception:
        pass

    datefmt = "%Y-%m-%d"
    matches = Match.objects.filter(starttime__gte=starttime.strftime(datefmt)) \
        .exclude(starttime__gt=endtime.strftime(datefmt)).order_by('starttime')

    if request.GET.get('f') == 'json':
        json_serializer = serializers.get_serializer("json")()
        response = HttpResponse()
        json_serializer.serialize(matches, fields=('id', 'poolroom', 'bonus', 'starttime', 'enrollfee', 'enrollfocal', 'rule', 'bonusdetail'), ensure_ascii=False, stream=response, indent=2, use_natural_keys=True)
        return response
    if view == 'map':
        page = 'match_map_v2.html'
    else:
        page = 'match_list.html'

    intervals = 30
    starttime2 = datetime.datetime.today()
    endtime2 = starttime2 + relativedelta(days=intervals)
    matchCountSummary = dict()
    rt = Match.objects.filter(starttime__gte=starttime2.strftime(datefmt)) \
         .exclude(starttime__gt=endtime2.strftime(datefmt))
    for match in rt:
        if match.starttime.strftime(datefmt) in matchCountSummary:
            matchCountSummary[match.starttime.strftime(datefmt)] += 1
        else:
            matchCountSummary[match.starttime.strftime(datefmt)] = 1
    topOneBonusSummary = Match.objects.values('starttime','bonus').filter(starttime__gte=starttime2.strftime(datefmt)) \
         .exclude(starttime__gt=endtime2.strftime(datefmt)).filter(bonus=Match.objects.filter(starttime__gte=starttime2.strftime(datefmt)) \
         .exclude(starttime__gt=endtime2.strftime(datefmt)).aggregate(Max('bonus'))['bonus__max'])

    def ValuesQuerySetToDict(vqs):
        return [{'bonus': item['bonus'], 'starttime': item['starttime'].strftime(datefmt)} for item in vqs]

    return render_to_response(templatepath + page,
                              {'matches': matches, 'startdate': starttime, 'enddate': endtime, 'STATIC_URL': STATIC_URL,
                               'intervals': intervals, 'matchsummary': matchCountSummary, 'bonussummary': simplejson.dumps(ValuesQuerySetToDict(topOneBonusSummary))},
                              context_instance=RequestContext(request))

def detail(request, matchid):
    match = get_object_or_404(Match, pk=matchid)

    if request.GET.get('f') == 'json':
        json_serializer = serializers.get_serializer("json")()
        response = HttpResponse()
        json_serializer.serialize([match], fields=('id', 'poolroom', 'bonus', 'starttime', 'description'), ensure_ascii=False, stream=response, indent=2, use_natural_keys=True)
        return response

    return render_to_response(templatepath + 'match_detail.html', {'match': match})