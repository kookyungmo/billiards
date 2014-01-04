# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2014年1月4日

@author: kane
'''
import datetime
from billiards.models import Challenge, ChallengeApply
from django.shortcuts import render_to_response, get_object_or_404
from billiards.settings import TEMPLATE_ROOT
from django.template.context import RequestContext
from StringIO import StringIO
from django.http import HttpResponse, HttpResponseForbidden
import json

from django.core.serializers.json import Serializer as JsonSerializer 
from django.utils.encoding import is_protected_type 
from django.utils import simplejson
from django.db.models.query_utils import Q
from billiards.location_convertor import bd2gcj, distance
class DisplayNameJsonSerializer(JsonSerializer): 

    def handle_field(self, obj, field): 
        value = field._get_val_from_obj(obj) 

        #If the object has a get_field_display() method, use it. 
        display_method = "get_%s_display" % field.name 
        if  hasattr(field, 'json_use_value') and getattr(field, 'json_use_value')() == False:
            self._current[field.name] = value
        elif hasattr(obj, display_method): 
            self._current[field.name] = getattr(obj, display_method)() 
        # Protected types (i.e., primitives like None, numbers, dates, 
        # and Decimals) are passed through as is. All other values are 
        # converted to string first. 
        elif is_protected_type(value): 
            self._current[field.name] = value 
        else: 
            self._current[field.name] = field.value_to_string(obj) 

def updateChallengeJsonStrApplyInfo(jsonstr, user, challenges):
    appliedChallenges = ChallengeApply.objects.filter(Q(challenge__in=challenges) & Q(user__exact=user))
    if len(appliedChallenges) > 0:
        challenges = simplejson.loads(jsonstr)
        for challengeApply in appliedChallenges:
            for challenge in challenges:
                if challengeApply.challenge.id == challenge['pk']:
                    challenge['fields']['applied'] = True
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

def index(request, lat = None, lng = None):
    if 'f' in request.GET and request.GET.get('f') == 'json':
        starttime = datetime.datetime.today()
        datefmt = "%Y-%m-%d"
        challenges = Challenge.objects.filter(starttime__gte=starttime.strftime(datefmt)).order_by('starttime')
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
        
    return render_to_response(TEMPLATE_ROOT + 'challenge.html',
                              {},
                              context_instance=RequestContext(request))
    
def applyChallenge(request, challengeid):
    if not request.user.is_authenticated():
        raise HttpResponseForbidden()
    
    challenge = get_object_or_404(Challenge, pk=challengeid)
    
    obj, created = ChallengeApply.objects.get_or_create(challenge=challenge, user=request.user,
                  defaults={'applytime': datetime.datetime.now()})
    
    addition = {'info_missing': False}
    if request.user.email == None or request.user.cellphone == None:
        addition['info_missing'] = True
    if obj != False:
        msg = {'rt': 2, 'msg': 'already applied'}
    elif created != False:
        msg = {'rt': 1, 'msg': 'applied'}
    return HttpResponse(json.dumps(dict(addition.items() + msg.items())), content_type="application/json")