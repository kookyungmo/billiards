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
from billiards.bcms import mail
from billiards import settings
from django.db.models.query_utils import Q
from billiards.location_convertor import gcj2bd

def index(request):
    poolroomusers = getPoolroom(request.user, (1|2))
    return render_to_response(TEMPLATE_ROOT + 'club/index.html', 
                              combinePageVariables({}, poolroomusers),
                              context_instance=RequestContext(request))

def getPoolroom(user, matchtype = 1):
    if not user.is_authenticated():
        raise PermissionDenied
    poolroomusers = PoolroomUser.objects.filter(user=user)
    if len(poolroomusers) == 0:
        raise PermissionDenied
    if (poolroomusers[0].type & matchtype) == 0:
        raise PermissionDenied
    return poolroomusers
 
def combinePageVariables(dict1, poolroomusers):
    if len(poolroomusers) > 0:
        groups = []
        for poolroomuser in poolroomusers:
            if poolroomuser.type == 2:
                groups.append(poolroomuser)
        return dict(dict1.items() + {'poolroomuser': list(poolroomusers)[0], 'groups': groups}.items())
    return dict1
    
def match(request):
    poolroomusers = getPoolroom(request.user)
    poolrooms = []
    for pu in poolroomusers:
        poolrooms.append(pu.poolroom)
    publishedMatches = Match.objects.filter(poolroom__in=poolrooms).filter(type=1).order_by('-starttime', 'status')
    return render_to_response(TEMPLATE_ROOT + 'club/match.html', 
                              combinePageVariables({'matches': publishedMatches}, poolroomusers),
                              context_instance=RequestContext(request))

class MatchForm(ModelForm):
    class Meta:
        model = Match

def saveMatch(request, poolroomid, match = None, organizer = 1, matchtype = 1):
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
           'organizer': organizer,
           'type': matchtype,
           }
    if match is None:
        data['poolroom'] = poolroomid
        data['status'] = 'approved'
        newmatch = MatchForm(data)
    else:
        data['status'] = request.POST['status']
        data['poolroom'] = poolroomid
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
    
def checkPoolroomUserByMatch(user, matchid, matchtype = 1):
    poolroomusers = getPoolroom(user, matchtype)
    match = get_object_or_404(Match, pk=matchid)
    if match.type != matchtype:
        raise PermissionDenied
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
    publishedChallenges = Challenge.objects.filter(Q(poolroom__in=poolrooms) & Q(source=1)).order_by('-starttime', 'status')
    return render_to_response(TEMPLATE_ROOT + 'club/challenge.html', 
                              combinePageVariables({'challenges': publishedChallenges}, poolroomusers),
                              context_instance=RequestContext(request))

class ChallengeForm(ModelForm):
    class Meta:
        model = Challenge
        
def saveChallenge(request, issuer, poolroom, challenge = None, source = 1, location = None, username = None, group = 1):
    starttime = datetime.datetime.fromtimestamp(float(request.POST['starttime'])/1000, pytz.timezone(TIME_ZONE))
    expiredtime = datetime.datetime.fromtimestamp(float(request.POST['expiredtime'])/1000, pytz.timezone(TIME_ZONE))
    data = {       
           'issuer_nickname': request.POST['nickname'],
           'level': request.POST['level'],
           'tabletype': request.POST['tabletype'],
           'rule': request.POST['rule'],
           'starttime': starttime,
           'expiretime': expiredtime,
           'source': source,
           'issuer': issuer,
           'issuer_contact': request.POST['contact'],
           'group': group,
           'username': username,
           }
    if location is not None:
        data['location'] = location
    if challenge is None:
        data['poolroom'] = poolroom.id
        if location is None:
            data['lat'] = poolroom.lat
            data['lng'] = poolroom.lng
            data['lat_baidu'] = poolroom.lat_baidu
            data['lng_baidu'] = poolroom.lng_baidu
        else:
            glocs = location.split(':')[0].split[',']
            data['lat'] = glocs[0]
            data['lng'] = glocs[1]
            baidu_loc = gcj2bd(float(data['lat']),float(data['lng']))
            data['lat_baidu'] = unicode(baidu_loc[0])
            data['lag_baidu'] = unicode(baidu_loc[1])
        data['status'] = 'waiting'
        newchallenge = ChallengeForm(data)
    else:
        data['status'] = request.POST['status']
        data['poolroom'] = challenge.poolroom.id
        data['lat'] = challenge.poolroom.lat
        data['lng'] = challenge.poolroom.lng
        data['lat_baidu'] = challenge.poolroom.lat_baidu
        data['lng_baidu'] = challenge.poolroom.lng_baidu
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
            return saveChallenge(request, "wechat:unknown", list(poolroomusers)[0].poolroom, username=request.user.username)
        except Exception, e:
            return HttpResponse(json.dumps({'rt': 0, 'msg': u'Invalid Arguments.'}), content_type="application/json")
    return render_to_response(TEMPLATE_ROOT + 'club/challenge_edit.html', 
                                  combinePageVariables({}, poolroomusers),
                                  context_instance=RequestContext(request))

def checkPoolroomUserByChallenge(user, challengeid):
    poolroomusers = getPoolroom(user)
    challenge = get_object_or_404(Challenge, pk=challengeid)
    for pu in poolroomusers:
        if pu.poolroom.id == challenge.poolroom.id and (pu.type & 1 > 0):
            return poolroomusers, challenge
    raise PermissionDenied

@ensure_csrf_cookie
def challenge_edit(request, challengeid):
    poolroomusers, challenge = checkPoolroomUserByChallenge(request.user, challengeid)
    if request.method == 'POST':
        try:
            return saveChallenge(request, "wechat:unknown", list(poolroomusers)[0].poolroom, challenge, username=request.user.username)
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
        if pu.poolroom.id == application.challenge.issuer.id and (pu.type & 1 > 0):
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
        if int(poolroomid) <= 0:
            # use any one for satisfying db design
            poolroom = Poolroom.objects.all()[:1][0]
            poolroomid = poolroom.id
        else:
            poolroom = get_object_or_404(Poolroom, pk=poolroomid)
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
            mail(settings.NOTIFICATION_EMAIL, 'New club application', '%s(%s) apply %s\'s %s.\r\n Justification: %s.' 
                 %(unicode(request.user), request.POST['realname'], poolroom.name, 'owner' if request.POST['club'] != -1 else 'group owner', request.POST['justification']))
            return HttpResponse(json.dumps({'rt': 1, 'msg': 'created'}), content_type="application/json")
        return HttpResponse(json.dumps(dict({'rt': 0}.items() + newapply.errors.items())), content_type="application/json")
    clubs = Poolroom.objects.all()
    return render_to_response(TEMPLATE_ROOT + 'club/apply.html', 
                                  {'clubs': clubs},
                                  context_instance=RequestContext(request))
    
def activity(request):
    poolroomusers = getPoolroom(request.user, 2)
    poolrooms = []
    for pu in poolroomusers:
        if pu.type == 2:
            poolrooms.append(pu.poolroom)
    publishedMatches = Match.objects.filter(poolroom__in=poolrooms).filter(organizer=poolroomusers[0].group).filter(type=2).order_by('-starttime', 'status')
    return render_to_response(TEMPLATE_ROOT + 'club/activity.html', 
                              combinePageVariables({'acitivies': publishedMatches}, poolroomusers),
                              context_instance=RequestContext(request))

@ensure_csrf_cookie
def activity_add(request):
    poolroomusers = getPoolroom(request.user, 2)
    if request.method == 'POST':
        try:
            poolroomid = int(request.POST['club'])
            for poolroomuser in poolroomusers:
                if poolroomuser.type == 2 and poolroomid == poolroomuser.poolroom.id: 
                    return saveMatch(request, poolroomid, organizer=poolroomuser.group.id, matchtype=2)
            raise PermissionDenied
        except PermissionDenied, e:
            raise e
        except Exception:     
            return HttpResponse(json.dumps({'rt': 0, 'msg': u'Invalid Arguments.'}), content_type="application/json")
    return render_to_response(TEMPLATE_ROOT + 'club/activity_edit.html', 
                                  combinePageVariables({}, poolroomusers),
                                  context_instance=RequestContext(request))
    
@ensure_csrf_cookie
def activity_edit(request, activityid):
    poolroomusers, activity = checkPoolroomUserByMatch(request.user, activityid, 2)
    if request.method == 'POST':
        try:
            if activity.type != 2:
                raise PermissionDenied
            poolroomid = int(request.POST['club'])
            for poolroomuser in poolroomusers:
                if poolroomuser.type == 2 and poolroomid == poolroomuser.poolroom.id: 
                    return saveMatch(request, poolroomid, activity, organizer=poolroomuser.group.id, matchtype=2)
            raise PermissionDenied
        except PermissionDenied, e:
            raise e
        except Exception:     
            return HttpResponse(json.dumps({'rt': 0, 'msg': u'Invalid Arguments.'}), content_type="application/json")
    return render_to_response(TEMPLATE_ROOT + 'club/activity_edit.html', 
                                  combinePageVariables({'activity': activity}, poolroomusers),
                                  context_instance=RequestContext(request))