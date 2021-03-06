# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2013年10月22日

@author: kane
'''
from StringIO import StringIO
import datetime
import json

from dateutil.relativedelta import relativedelta
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.db.models.aggregates import Max
from django.db.models.query_utils import Q
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template.context import RequestContext
from django.utils import simplejson
import pytz

from billiards import settings
from billiards.commons import tojson
from billiards.models import Match, MatchEnroll, \
     match_fields
from billiards.settings import TEMPLATE_ROOT, TIME_ZONE


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

datefmt = "%Y-%m-%d"
def set_to_midnight(dt):
    midnight = datetime.time(0)
    localtz = pytz.timezone(settings.TIME_ZONE)
    return localtz.localize(datetime.datetime.combine(dt.date(), midnight))

def getQueryCriteria(starttime, endtime):
    return Q(starttime__gte=set_to_midnight(starttime)) & Q(status='approved') & Q(starttime__lt=set_to_midnight(endtime))

def getMatchByRequest(request, starttime = None, endtime = None, deltadays = 1):
    if starttime == None:
        starttimenative = datetime.datetime.today()
        localtz = pytz.timezone(settings.TIME_ZONE)
        starttime = localtz.localize(starttimenative)
        try:
            if request.GET.get('starttime') is not None:
                starttime = set_to_midnight(datetime.datetime.utcfromtimestamp(float(request.GET.get('starttime'))))
        except Exception:
            pass
    
    if endtime == None:
        endtime = starttime + relativedelta(days=deltadays)
        try:
            if request.GET.get('endtime') is not None:
                endtime = datetime.datetime.utcfromtimestamp(float(request.GET.get('endtime')))
        except Exception:
            pass

    query = getQueryCriteria(starttime, endtime)
    matches = Match.objects.filter(query).order_by('starttime')
    return matches, starttime, endtime
    
def index(request, view = None):
    starttime = None
    
    intervals = 7
    starttime2 = datetime.datetime.today()
    endtime2 = starttime2 + relativedelta(days=intervals)
    
    if 's' in request.GET:
        try:
            starttimeS = datetime.datetime.utcfromtimestamp(float(request.GET.get('s')))
            if set_to_midnight(starttime2) <= set_to_midnight(starttimeS) <= set_to_midnight(endtime2):
                starttime = starttimeS
        except Exception:
            pass
    matches, starttime, endtime = getMatchByRequest(request, starttime)
                  
    if request.GET.get('f') == 'json':
        jsonstr = tojson(matches, match_fields)
        if request.user.is_authenticated():
            jsonstr = updateMatchJsonStrEnrollInfo(jsonstr, request.user, matches)
        return HttpResponse(jsonstr)
    
    page = 'match.html'
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
                              {'matches': matches, 'startdate': starttime2, 'enddate': endtime2,
                               'intervals': intervals, 'matchsummary': matchCountSummary, 'bonussummary': simplejson.dumps(ValuesQuerySetToDict(topOneBonusSummary)),
                              },
                              context_instance=RequestContext(request))
def getMatch(matchid):
    return get_object_or_404(Match, pk=matchid, status='approved')

def detail(request, matchid):
    match = getMatch(matchid)
    
    if match.type == 2:
        return redirect('activity_detail', matchid=matchid)
        
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
    

def activity(request, matchid):
    match = getMatch(matchid)
    
    if match.type == 1:
        return redirect('match_detail', matchid=matchid)
        
    return render_to_response(TEMPLATE_ROOT + 'activity_detail.html', {'match': match},
                              context_instance=RequestContext(request))

def enroll(request, matchid):
    if not request.user.is_authenticated():
        raise PermissionDenied
    
    match = getMatch(matchid)
    
    if match.is_expired:
        return HttpResponse(json.dumps({'rt': 3, 'msg': 'match is expired'}), content_type="application/json")
    elif match.status != 'approved':
        return HttpResponse(json.dumps({'rt': 4, 'msg': 'match is invalid'}), content_type="application/json")
    elif match.type == 2:
        return HttpResponse(json.dumps({'rt': 5, 'msg': 'can not enroll activity'}), content_type="application/json")
    
    obj, created = MatchEnroll.objects.get_or_create(match=match, user=request.user,
                  defaults={'enrolltime': datetime.datetime.utcnow().replace(tzinfo=pytz.timezone(TIME_ZONE))})
    
    if obj != False:
        msg = {'rt': 2, 'msg': 'already enrolled'}
    elif created != False:
        msg = {'rt': 1, 'msg': 'enrolled'}
    return HttpResponse(json.dumps(msg), content_type="application/json")

def redbull_2014_05(request):
    if 'f' in request.GET and request.GET.get('f') == 'json':
        redbull_matches = Match.objects.filter(Q(flags=Match.flags.redbull)).order_by('starttime')
        json_serializer = serializers.get_serializer("json")()
        stream = StringIO()
        json_serializer.serialize(redbull_matches, fields=match_fields, ensure_ascii=False, stream=stream, indent=2, use_natural_keys=True)
        jsonstr = stream.getvalue()
        return HttpResponse(jsonstr)
    return render_to_response(TEMPLATE_ROOT + 'redbull/match_poolroom.html', {},
            context_instance=RequestContext(request))

def winners(request):
    return render_to_response(TEMPLATE_ROOT + 'redbull/match_winners.html', context_instance=RequestContext(request))
