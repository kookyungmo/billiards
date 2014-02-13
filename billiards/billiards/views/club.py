# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2014年1月10日

@author: kane
'''
from django.http import HttpResponse
from billiards.models import PoolroomUser, Match, MatchEnroll, Challenge,\
    ChallengeApply, Poolroom, PoolroomUserApply
from django.template.context import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from billiards.settings import TEMPLATE_ROOT, TIME_ZONE
from django.forms.models import ModelForm
import json
import datetime
from django.utils.timezone import pytz
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.views.decorators.csrf import ensure_csrf_cookie

def index(request):
    poolroomusers = getPoolroom(request.user)
    return render_to_response(TEMPLATE_ROOT + 'club/index.html', 
                              combinePageVariables({}, poolroomusers),
                              context_instance=RequestContext(request))

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
           'organizer': 1,
           'type': 1,
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

@ensure_csrf_cookie
def match_add(request):
    poolroomusers = getPoolroom(request.user)
    if request.method == 'POST':
        try:
            return saveMatch(request, list(poolroomusers)[0].poolroom.id)
        except Exception:     
            return HttpResponse(json.dumps({'rt': 0, 'msg': u'Invalid Arguments.'}), content_type="application/json")
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

@ensure_csrf_cookie
def match_edit(request, matchid):
    poolroomusers, match = checkPoolroomUserByMatch(request.user, matchid)
    if request.method == 'POST':
        try:
            return saveMatch(request, list(poolroomusers)[0].poolroom.id, match)
        except Exception:     
            return HttpResponse(json.dumps({'rt': 0, 'msg': u'Invalid Arguments.'}), content_type="application/json")
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
    poolroomusers = getPoolroom(request.user)
    poolrooms = []
    for pu in poolroomusers:
        poolrooms.append(pu.poolroom)
    publishedChallenges = Challenge.objects.filter(issuer__in=poolrooms).order_by('-starttime', 'status')
    return render_to_response(TEMPLATE_ROOT + 'club/challenge.html', 
                              combinePageVariables({'challenges': publishedChallenges}, poolroomusers),
                              context_instance=RequestContext(request))

class ChallengeForm(ModelForm):
    class Meta:
        model = Challenge
        
def saveChallenge(request, poolroomid, challenge = None):
    starttime = datetime.datetime.fromtimestamp(float(request.POST['starttime'])/1000, pytz.timezone(TIME_ZONE))
    expiredtime = datetime.datetime.fromtimestamp(float(request.POST['expiredtime'])/1000, pytz.timezone(TIME_ZONE))
    data = {       
           'issuer_nickname': request.POST['nickname'],
           'level': request.POST['level'],
           'tabletype': request.POST['tabletype'],
           'rule': request.POST['rule'],
           'starttime': starttime,
           'expiretime': expiredtime,
           }
    if challenge is None:
        data['issuer'] = poolroomid
        data['status'] = 'waiting'
        newchallenge = ChallengeForm(data)
    else:
        data['status'] = request.POST['status']
        data['issuer'] = challenge.issuer.id
        newchallenge = ChallengeForm(data=data, instance=challenge)
    if newchallenge.is_valid():
        newchallenge.save()
        return HttpResponse(json.dumps({'rt': 1, 'msg': 'created'}), content_type="application/json")
    return HttpResponse(json.dumps(dict({'rt': 0}.items() + newchallenge.errors.items())), content_type="application/json")

@ensure_csrf_cookie   
def challenge_add(request):
    poolroomusers = getPoolroom(request.user)
    if request.method == 'POST':
        try:
            return saveChallenge(request, list(poolroomusers)[0].poolroom.id)
        except Exception:
            return HttpResponse(json.dumps({'rt': 0, 'msg': u'Invalid Arguments.'}), content_type="application/json")
    return render_to_response(TEMPLATE_ROOT + 'club/challenge_edit.html', 
                                  combinePageVariables({}, poolroomusers),
                                  context_instance=RequestContext(request))

def checkPoolroomUserByChallenge(user, challengeid):
    poolroomusers = getPoolroom(user)
    challenge = get_object_or_404(Challenge, pk=challengeid)
    for pu in poolroomusers:
        if pu.poolroom.id == challenge.issuer.id:
            return poolroomusers, challenge
    raise PermissionDenied

@ensure_csrf_cookie
def challenge_edit(request, challengeid):
    poolroomusers, challenge = checkPoolroomUserByChallenge(request.user, challengeid)
    if request.method == 'POST':
        try:
            return saveChallenge(request, list(poolroomusers)[0].poolroom.id, challenge)
        except Exception:     
            return HttpResponse(json.dumps({'rt': 0, 'msg': u'Invalid Arguments.'}), content_type="application/json")
    return render_to_response(TEMPLATE_ROOT + 'club/challenge_edit.html', 
                                  combinePageVariables({'ch': challenge}, poolroomusers),
                                  context_instance=RequestContext(request))

def challenge_enroll(request, challengeid):
    poolroomusers, challenge = checkPoolroomUserByChallenge(request.user, challengeid)
    applications = ChallengeApply.objects.filter(challenge=challenge).order_by('-applytime')
    return render_to_response(TEMPLATE_ROOT + 'club/challenge_applications.html', 
                                  combinePageVariables({'ch': challenge, 'applications': applications}, poolroomusers),
                                  context_instance=RequestContext(request))

def checkPoolroomUserByChallengeApp(user, appid):
    poolroomusers = getPoolroom(user)
    application = get_object_or_404(ChallengeApply, pk=appid)
    for pu in poolroomusers:
        if pu.poolroom.id == application.challenge.issuer.id:
            return poolroomusers, application.challenge, application
    raise PermissionDenied

def challengeapp_accept(request, appid):
    poolroomusers, challenge, app = checkPoolroomUserByChallengeApp(request.user, appid)
    if app.status != 'accepted':
        app.status = 'accepted'
        app.save()
        rt = {'rt': 1, 'msg': 'app is accepted'}
    else:
        rt = {'rt': 2, 'msg': 'app has been accepted'}
    return HttpResponse(json.dumps(rt), content_type="application/json")

@transaction.commit_on_success
def challengeapp_reject(request, appid):
    poolroomusers, challenge, app = checkPoolroomUserByChallengeApp(request.user, appid)
    if app.status != 'rejected':
        app.status = 'rejected'
        app.save()
        if not challenge.is_expired:
            challenge.status = 'waiting'
            challenge.save()
        rt = {'rt': 1, 'msg': 'app is rejected'}
    else:
        rt = {'rt': 2, 'msg': 'app has been rejected'}
    return HttpResponse(json.dumps(rt), content_type="application/json")

class PoolroomUserApplyForm(ModelForm):
    class Meta:
        model = PoolroomUserApply
     
@ensure_csrf_cookie   
def club_apply(request):
    if not request.user.is_authenticated():
        raise PermissionDenied
    
    if request.method == 'POST':
        poolroomid = request.POST['club']
        if int(poolroomid) == 0:
            # use other for satisfying db design
            poolroomid = Poolroom.objects.all()[:1][0].id
        data = {
           'poolroom': poolroomid,
           'poolroomname_userinput': 'null' if request.POST['club_userinput'] == '' else request.POST['club_userinput'],
           'user': request.user.id,
           'realname': request.POST['realname'],
           'cellphone': request.POST['cellphone'],
           'email': request.POST['email'],
           'justification': request.POST['justification'],
           'applytime': datetime.datetime.utcnow().replace(tzinfo=pytz.timezone(TIME_ZONE)),
           'status': 'submitted',
           }
        newapply = PoolroomUserApplyForm(data)
        if newapply.is_valid():
            newapply.save()
            return HttpResponse(json.dumps({'rt': 1, 'msg': 'created'}), content_type="application/json")
        return HttpResponse(json.dumps(dict({'rt': 0}.items() + newapply.errors.items())), content_type="application/json")
    clubs = Poolroom.objects.all()
    return render_to_response(TEMPLATE_ROOT + 'club/apply.html', 
                                  {'clubs': clubs},
                                  context_instance=RequestContext(request))