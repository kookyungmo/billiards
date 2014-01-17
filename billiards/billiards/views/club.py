# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2014年1月10日

@author: kane
'''
from django.http import HttpResponse
from billiards.models import PoolroomUser, Match, MatchEnroll
from django.template.context import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from billiards.settings import TEMPLATE_ROOT, TIME_ZONE
from django.forms.models import ModelForm
import json
import datetime
from django.utils.timezone import pytz
from django.core.exceptions import PermissionDenied

def getPoolroom(user):
    if not user.is_authenticated():
        raise PermissionDenied
    poolroomusers = PoolroomUser.objects.filter(user=user)
    if len(poolroomusers) == 0:
        raise PermissionDenied
    return poolroomusers
 
def combinePageVariables(dict1, poolroomusers):
    if len(poolroomusers) > 0:
        return dict(dict1.items() + {'poolroomuser': list(poolroomusers)[0]}.items())
    return dict1
    
def match(request):
    poolroomusers = getPoolroom(request.user)
    poolrooms = []
    for pu in poolroomusers:
        poolrooms.append(pu.poolroom)
    publishedMatches = Match.objects.filter(poolroom__in=poolrooms).order_by('-starttime', 'status')
    return render_to_response(TEMPLATE_ROOT + 'club/match.html', 
                              combinePageVariables({'matches': publishedMatches}, poolroomusers),
                              context_instance=RequestContext(request))

class MatchForm(ModelForm):
    class Meta:
        model = Match

def saveMatch(request, poolroomid, match = None):
    attributelist = []
    if request.POST['groupon'] == 'true':
        attributelist.append('groupon')
    if request.POST['coupon'] == 'true':
        attributelist.append('coupon')
    starttime = datetime.datetime.fromtimestamp(float(request.POST['matchtime'])/1000, pytz.timezone(TIME_ZONE))
    data = {       
           'title': request.POST['matchtitle'],
           'bonus': request.POST['cashbonus'],
           'rechargeablecard': request.POST['cardbonous'],
           'otherprize': request.POST['otherbonous'],
           'bonusdetail': request.POST['bonusdetail'],
           'rule': request.POST['matchrule'],
           'description': request.POST['description'],
           'starttime': starttime,
           'enrollfee': request.POST['enrollfee'],
           'enrollfocal': request.POST['enrollfocal'],
           'flags': attributelist,
           }
    if match is None:
        data['poolroom'] = poolroomid
        data['status'] = 'approved'
        newmatch = MatchForm(data)
    else:
        data['status'] = request.POST['status']
        data['poolroom'] = match.poolroom.id
        newmatch = MatchForm(data=data, instance=match)
    if newmatch.is_valid():
        newmatch.save()
        return HttpResponse(json.dumps({'rt': 1, 'msg': 'created'}), content_type="application/json")
    return HttpResponse(json.dumps(dict({'rt': 0}.items() + newmatch.errors.items())), content_type="application/json")

def match_add(request):
    poolroomusers = getPoolroom(request.user)
    if request.method == 'POST':
        try:
            return saveMatch(request, list(poolroomusers)[0].poolroom.id)
        except Exception:     
            return HttpResponse(json.dumps({'rt': 0, 'msg': u'Invalid Arguments.'}, content_type="application/json"))
    return render_to_response(TEMPLATE_ROOT + 'club/match_edit.html', 
                                  combinePageVariables({}, poolroomusers),
                                  context_instance=RequestContext(request))
    
def checkPoolroomUserByMatch(user, matchid):
    poolroomusers = getPoolroom(user)
    match = get_object_or_404(Match, pk=matchid)
    for pu in poolroomusers:
        if pu.poolroom.id == match.poolroom.id:
            return poolroomusers, match
    raise PermissionDenied

def match_edit(request, matchid):
    poolroomusers, match = checkPoolroomUserByMatch(request.user, matchid)
    if request.method == 'POST':
        try:
            return saveMatch(request, list(poolroomusers)[0].poolroom.id, match)
        except Exception:     
            return HttpResponse(json.dumps({'rt': 0, 'msg': u'Invalid Arguments.'}, content_type="application/json"))
    return render_to_response(TEMPLATE_ROOT + 'club/match_edit.html', 
                                  combinePageVariables({'match': match}, poolroomusers),
                                  context_instance=RequestContext(request))
    
def match_enroll(request, matchid):
    poolroomusers, match = checkPoolroomUserByMatch(request.user, matchid)
    enrolments = MatchEnroll.objects.filter(match=match).order_by('-enrolltime')
    return render_to_response(TEMPLATE_ROOT + 'club/match_enroll.html', 
                                  combinePageVariables({'match': match, 'enrolments': enrolments}, poolroomusers),
                                  context_instance=RequestContext(request))

def challenge(request):
    pass