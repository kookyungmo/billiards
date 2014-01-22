# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2013年10月22日

@author: kane
'''
from django.shortcuts import render_to_response, get_object_or_404
from billiards.models import Match, MatchEnroll,\
    DisplayNameJsonSerializer, match_fields
import datetime
from dateutil.relativedelta import relativedelta
from django.core import serializers
from django.http import HttpResponse
from django.template.context import RequestContext
from django.db.models.aggregates import Max
from django.utils import simplejson
from billiards.settings import TEMPLATE_ROOT, TIME_ZONE
import json
from django.db.models.query_utils import Q
from StringIO import StringIO
from django.core.exceptions import PermissionDenied
import pytz
from django.db.models.query import QuerySet, ValuesQuerySet

def updateMatchJsonStrEnrollInfo(matchjsonstr, user, matchArray):
    enrolledMatch = MatchEnroll.objects.filter(Q(match__in=matchArray) & Q(user__exact=user))
    if len(enrolledMatch) > 0:
        matches = simplejson.loads(matchjsonstr)
        for enrollinfo in enrolledMatch:
            for match in matches:
                if enrollinfo.match.id == match['pk']:
                    match['fields']['enrolled'] = True
                    break
        matchjsonstr = simplejson.dumps(matches)
    return matchjsonstr

def updateMatchQuerySetEnrollInfo(matchQuerySet, user):
    enrolledMatch = MatchEnroll.objects.filter(Q(match__in=matchQuerySet) & Q(user__exact=user))
    if len(enrolledMatch) > 0:
        for enrollinfo in enrolledMatch:
            for match in matchQuerySet:
                if enrollinfo.match.id == match.id:
                    setattr(match, 'enrolled', True)
                    break
    return matchQuerySet

def tojson(data, fields = None):
    newdata = data
    if not isinstance(newdata, (QuerySet, ValuesQuerySet)):
        newdata = [data]
    json_serializer = DisplayNameJsonSerializer()
    stream = StringIO()
    json_serializer.serialize(newdata, fields=fields, stream=stream,
            ensure_ascii=False, use_natural_keys=True)
    return stream.getvalue()

datefmt = "%Y-%m-%d"
def getQueryCriteria(starttime, endtime):
    return Q(starttime__gte=starttime.strftime(datefmt)) & Q(status='approved') & Q(starttime__lt=endtime.strftime(datefmt))
    
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

    query = getQueryCriteria(starttime, endtime)
    matches = Match.objects.filter(query).order_by('starttime')
                  
    if request.GET.get('f') == 'json':
        jsonstr = tojson(matches, match_fields)
        if request.user.is_authenticated():
            jsonstr = updateMatchJsonStrEnrollInfo(jsonstr, request.user, matches)
        return HttpResponse(jsonstr)
    if view == 'map':
        page = 'match_map_v2.html'
    else:
        page = 'match_list.html'

    intervals = 7
    starttime2 = datetime.datetime.today()
    endtime2 = starttime2 + relativedelta(days=intervals)
    query2 = getQueryCriteria(starttime2, endtime2)
    matchCountSummary = dict()
    rt = Match.objects.filter(query2)
    for match in rt:
        if match.starttime.strftime(datefmt) in matchCountSummary:
            matchCountSummary[match.starttime.strftime(datefmt)] += 1
        else:
            matchCountSummary[match.starttime.strftime(datefmt)] = 1
    topOneBonusSummary = Match.objects.values('starttime','bonus').filter(query2).filter(bonus=Match.objects.filter(query2).aggregate(Max('bonus'))['bonus__max'])
    def ValuesQuerySetToDict(vqs):
        return [{'bonus': item['bonus'], 'starttime': item['starttime'].strftime(datefmt)} for item in vqs]
    
    return render_to_response(TEMPLATE_ROOT + page,
                              {'matches': matches, 'startdate': starttime, 'enddate': endtime,
                               'intervals': intervals, 'matchsummary': matchCountSummary, 'bonussummary': simplejson.dumps(ValuesQuerySetToDict(topOneBonusSummary)),
                              },
                              context_instance=RequestContext(request))
def getMatch(matchid):
    return get_object_or_404(Match, pk=matchid, status='approved')

def detail(request, matchid):
    match = getMatch(matchid)
        
    if request.GET.get('f') == 'json':
        json_serializer = serializers.get_serializer("json")()
        stream = StringIO()
        json_serializer.serialize([match], fields=('id', 'poolroom', 'title', 'bonus', 'starttime', 'description'), ensure_ascii=False, stream=stream, indent=2, use_natural_keys=True)
        jsonstr = stream.getvalue()
        if request.user.is_authenticated():
            jsonstr = updateMatchJsonStrEnrollInfo(jsonstr, request.user, [match])
        return HttpResponse(jsonstr)
    
    if request.user.is_authenticated():
        match = updateMatchQuerySetEnrollInfo([match], request.user)[0]
        
    return render_to_response(TEMPLATE_ROOT + 'match_detail.html', {'match': match},
                              context_instance=RequestContext(request))

def enroll(request, matchid):
    if not request.user.is_authenticated():
        raise PermissionDenied
    
    match = getMatch(matchid)
    
    if match.is_expired:
        return HttpResponse(json.dumps({'rt': 3, 'msg': 'match is expired'}), content_type="application/json")
    elif match.status != 'approved':
        return HttpResponse(json.dumps({'rt': 4, 'msg': 'match is invalid'}), content_type="application/json")
    
    obj, created = MatchEnroll.objects.get_or_create(match=match, user=request.user,
                  defaults={'enrolltime': datetime.datetime.utcnow().replace(tzinfo=pytz.timezone(TIME_ZONE))})
    
    if obj != False:
        msg = {'rt': 2, 'msg': 'already enrolled'}
    elif created != False:
        msg = {'rt': 1, 'msg': 'enrolled'}
    return HttpResponse(json.dumps(msg), content_type="application/json")
