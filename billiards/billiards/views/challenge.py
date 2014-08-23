# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2014年1月4日

@author: kane
'''
import datetime
from billiards.models import Challenge, ChallengeApply,\
    DisplayNameJsonSerializer, Poolroom, Group
from django.shortcuts import render_to_response, get_object_or_404, redirect
from billiards.settings import TEMPLATE_ROOT, TIME_ZONE, PREFER_LOGIN_SITE
from django.template.context import RequestContext
from StringIO import StringIO
from django.http import HttpResponse, Http404
import json
from django.utils import simplejson
from django.db.models.query_utils import Q
from billiards.location_convertor import bd2gcj, distance, gcj2bd
from django.db import transaction, connection, utils
import pytz
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from billiards.views.poolroom import getNearbyPoolrooms, getPoolroomByUUID
from billiards.views.club import challenge, saveChallenge, saveChallenge2
from urlparse import urlparse
from django.core.urlresolvers import reverse
from django.core.cache import cache
from billiards.commons import KEY_PREFIX, forceLogin
import uuid
from django.contrib.auth.models import User
from billiards.annotation import deprecated
from billiards.templatetags.extras import decodeunicode

def updateChallengeJsonStrApplyInfo(jsonstr, user, challenges):
    appliedChallenges = ChallengeApply.objects.filter(Q(challenge__in=challenges) & Q(user__exact=user))
    if len(appliedChallenges) > 0:
        challenges = simplejson.loads(jsonstr)
        for challengeApply in appliedChallenges:
            for challenge in challenges:
                if challengeApply.challenge.id == challenge['pk']:
                    challenge['fields']['applied'] = True
                    challenge['fields']['applystatus'] = challengeApply.status
                    break
        jsonstr = simplejson.dumps(challenges)
    return jsonstr

def updateChallengeJsonStrDistance(jsonstr, lat, lng):
    challenges = simplejson.loads(jsonstr)
    gp = bd2gcj(lat, lng)
    for challenge in challenges:
        gp2 = bd2gcj(challenge.fields.issuer.lat, challenge.fields.issuer.lng)
        challenge['fields']['distance'] = distance(gp[0], gp[1], gp2[0], gp2[1])
    jsonstr = simplejson.dumps(challenges)
    return jsonstr

def getChallenge(cid):
    return get_object_or_404(Challenge, pk=cid)

def index(request, lat = None, lng = None, group = 1):
    if 'f' in request.GET and request.GET.get('f') == 'json':
        starttime = datetime.datetime.today()
        datefmt = "%Y-%m-%d"
        challenges = Challenge.objects.filter(Q(starttime__gte=starttime.strftime(datefmt)) & Q(group=group)).order_by('starttime')
        json_serializer = DisplayNameJsonSerializer()
        stream = StringIO()
        json_serializer.serialize(challenges, ensure_ascii=False, stream=stream, indent=2, use_natural_keys=True)
        jsonstr = stream.getvalue()
        # calculate it in client
#         if lat is not None and lng is not None:
#             jsonstr = updateChallengeJsonStrDistance(jsonstr, lat, lng)
        if request.user.is_authenticated():
            jsonstr = updateChallengeJsonStrApplyInfo(jsonstr, request.user, challenges)
        return HttpResponse(jsonstr)
    gobj = None
    if group is not None and int(group) != 1:
        gobj = get_object_or_404(Group, id=group, status=1)
    if lat is not None and lng is not None:
        baiduLocs = gcj2bd(float(lat), float(lng))
        lat = baiduLocs[0]
        lng = baiduLocs[1]
    return render_to_response(TEMPLATE_ROOT + 'challenge.html',
                              {'lat': lat, 'lng': lng, 'gid': group if group != None else 1, 'group': gobj},
                              context_instance=RequestContext(request))

@deprecated
@transaction.commit_on_success
def applyChallenge(request, challengeid):
    if not request.user.is_authenticated():
        raise PermissionDenied
    try:
        challenge = Challenge.objects.select_for_update().get(pk=challengeid)
        if challenge.status == 'matched':
            msg = {'rt': 4, 'msg': 'already match'}
        elif challenge.is_expired:
            msg = {'rt': 3, 'msg': 'already expired'}
        else:
            obj, created = ChallengeApply.objects.get_or_create(challenge=challenge, user=request.user,
                      defaults={'applytime': datetime.datetime.utcnow().replace(tzinfo=pytz.timezone(TIME_ZONE))})
            if created and obj != None:
                challenge.status = 'matched'
                challenge.save()
                msg = {'rt': 1, 'msg': 'applied'}
            elif obj != None:
                msg = {'rt': 2, 'msg': 'already applied'}
            else:
                msg = {'rt': -1, 'msg': 'unknown error'}
        return HttpResponse(json.dumps(msg.items()), content_type="application/json")
    except Challenge.DoesNotExist:
        raise Http404
    
@csrf_exempt
def publish(request, group = None, lat = None, lng = None, distance = 3):
    if request.method == 'POST':
        try:
            poolroomid = int(request.POST['poolroom'])
            location = None
            if poolroomid == -1:
                location = "{0},{1}".format(lat, lng)
                poolroom = Poolroom.objects.all()[:1].get()
            elif poolroomid == 0:
                location = u"{0},{1}:{2}".format(lat, lng, request.POST['location'])
                poolroom = Poolroom.objects.all()[:1].get()
            else:
                try:
                    poolroom = Poolroom.objects.get(id=poolroomid)
                except Poolroom.DoesNotExist:
                    location = "{0},{1}".format(lat, lng)
                    poolroom = Poolroom.objects.all()[:1].get()
            username = None
            if request.user.is_authenticated():
                username = request.user.username
            issuer = 'unknown'
            try:
                issuer = request.POST['user']
            except KeyError:
                pass
            issuer = 'wechat:%s' %(issuer)
            group = 1
            try:
                group = int(request.POST['type'])
            except KeyError:
                pass
            return saveChallenge(request, issuer, poolroom, None, 2, location, username, group)
        except Exception:
            return HttpResponse(json.dumps({'rt': 0, 'msg': u'Invalid Arguments.'}), content_type="application/json")
    gobj = None
    if group is not None and int(group) != 1:
        gobj = get_object_or_404(Group, id=group, status=1)
    nearbypoolrooms = getNearbyPoolrooms(lat, lng, distance)
    username = 'unknown'
    try:
        username = request.GET['uid']
    except KeyError:
        pass
    return render_to_response(TEMPLATE_ROOT + 'challenge_application.html', 
                                  {'poolrooms': nearbypoolrooms, 'lat': lat, 'lng': lng, 'username': username, 'gid': group if group != None else 1, 'group': gobj}, context_instance=RequestContext(request))
    
def detail(request, challengeid):
    challenge = getChallenge(challengeid)
    group = challenge.group
    if challenge.lng_baidu is not None:
        location = "%s,%s" %(challenge.lng_baidu, challenge.lat_baidu)
    else:
        location = "%s,%s" %(challenge.poolroom.lng_baidu, challenge.poolroom.lat_baidu)
    locationtext = None
    if challenge.source == 2 and challenge.location != '':
        locationtexts = challenge.location.split(':')
        if len(locationtexts) > 1:
            locationtext = locationtexts[1]
            if challenge.lng_baidu is None:
                latlng = locationtexts[0].split(",")
                location = "%s,%s" %(latlng[1], latlng[2])
    url = request.build_absolute_uri(reverse('challenge_detail', args=[challengeid]))
    return render_to_response(TEMPLATE_ROOT + 'challenge_detail.html', {'cha': challenge, 'location': location, 'locationtext': locationtext, 'url': url,
                                'contact': urlparse(challenge.issuer_contact), 'gid': group.id, 'group': group },
                              context_instance=RequestContext(request))
    
def getNearbyChallenges(lat, lng, distance, datetime, group = 1):
    return Challenge.objects.filter(Q(group=group) & Q(expiretime__gt=datetime)).filter(geolocation__distance_lt=((lat, lng), distance)).order_by_distance()

@csrf_exempt
def wechatpublish(request):
    if request.user.is_authenticated() and request.user.site_name.startswith(PREFER_LOGIN_SITE):
        if request.method == 'POST':
            try:
                poolroom = getPoolroomByUUID(uuid.UUID(request.POST['poolroom']))
                nickname = request.user.nickname
                issuer = 'wechat:%s' %(request.user.username)
                group = 1
                try:
                    group = int(request.POST['type'])
                except KeyError:
                    pass
                
                starttime = datetime.datetime.fromtimestamp(float(request.POST['starttime'])/1000, pytz.timezone(TIME_ZONE))
                expiredtime = datetime.datetime.fromtimestamp(float(request.POST['expiredtime'])/1000, pytz.timezone(TIME_ZONE))
                participants = int(request.POST['participants'])
    
                return saveChallenge2(issuer, poolroom, starttime, expiredtime, nickname, 'professional', 'pocket', 'default rule', 'wechat:%s' %(nickname),
                                      'waiting', None, 2, None, request.user.username, group, participants)
            except Exception, e:
                return HttpResponse(json.dumps({'rt': 0, 'msg': str(e)}), content_type="application/json")
            
        challenges = Challenge.objects.filter(Q(username=request.user.username) & Q(expiretime__gt=datetime.datetime.utcnow()))    
        latlngstr = cache.get(KEY_PREFIX %('latlng', request.user.username))
        NEARBY = True
        if latlngstr == None:
            nearbypoolrooms = Poolroom.objects.filter(exist=1).order_by('-rating')[:15]
            NEARBY = False
        else:
            lat, lng = latlngstr.split(',', 1)
            nearbypoolrooms = getNearbyPoolrooms(lat, lng, 5)
        return render_to_response(TEMPLATE_ROOT + 'challenge_wechat_application.html', 
            {'poolrooms': nearbypoolrooms, 'isNearby': NEARBY, 'challenges': challenges}, context_instance=RequestContext(request))
        
    return forceLogin(request, PREFER_LOGIN_SITE)

def getChallengeByUUID(uuidstr):
    return get_object_or_404(Challenge, uuid=uuid.UUID(uuidstr))

@csrf_exempt
def detail_uuid(request, uuid):
    challenge = getChallengeByUUID(uuid)
    issuer = User.objects.get(username=challenge.username)
    hours, minutes = challenge.availableTime
    isEnrolled = any(request.user == enroll.user for enroll in challenge.participants)
    return render_to_response(TEMPLATE_ROOT + 'challenge_wechat_detail.html', 
        {'cha': challenge, 'issuer': issuer, 'hours': hours, 'minutes': minutes, "isEnrolled": isEnrolled,
         'preferSite': PREFER_LOGIN_SITE, 'pagetitle': u'%s邀请小伙伴们到%s打台球' %(decodeunicode(issuer.nickname), challenge.poolroom.name),
         'unavailable': (challenge.status == 'closed' or challenge.is_expired or challenge.status == 'expired')}, 
        context_instance=RequestContext(request))
    
@csrf_exempt
def apply_uuid(request, uuid):
    if not request.user.is_authenticated():
        raise PermissionDenied
    try:
        challenge = getChallengeByUUID(uuid)
        msg = None
        if challenge.status == 'matched':
            msg = {'rt': 4, 'msg': 'already match'}
        elif challenge.is_expired:
            msg = {'rt': 3, 'msg': 'already expired'}
        elif challenge.username == request.user.username:
            msg = {'rt': 6, 'msg': 'you are the host'}
        else:
            try:
                cursor = connection.cursor()
                query = '''INSERT INTO challenge_apply(challenge_id, user_id, applytime,status) 
                    SELECT %s, %s, '%s', 'accepted' FROM challenge WHERE (SELECT COUNT(*) FROM challenge_apply WHERE challenge_id = %s) < %s limit 1;''' %(
                    challenge.id, request.user.id, datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), challenge.id, challenge.participant_count)
                cursor.execute(query)
                transaction.commit()
                if cursor.rowcount == 1:
                    msg = {'rt': 1, 'msg': 'applied'}
                elif cursor.rowcount == 0:
                    msg = {'rt': 5, 'msg': 'no enough seat'}
                else:
                    msg = {'rt': -1, 'msg': 'unknown backend error'}
            except utils.IntegrityError:
                msg = {'rt': 2, 'msg': 'already applied'}
        if request.method == 'GET':
            return redirect('challenge_detail_uuid', uuid=str(uuid))
        return HttpResponse(json.dumps(msg.items()), content_type="application/json")
    except Challenge.DoesNotExist:
        raise Http404
