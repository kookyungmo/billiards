# -*- coding: utf-8 -*-
# encoding: utf-8
'''

@author: kane
'''

from django.http import HttpResponse
from billiards.models import Poolroom, PoolroomEquipment
from django.shortcuts import get_object_or_404, render_to_response
from django.core import serializers
from django.template.context import RequestContext
from billiards.settings import TEMPLATE_ROOT
from django.db import models

def more(request, poolroomid):
    poolroom = get_object_or_404(Poolroom, pk=poolroomid)

    equipments = PoolroomEquipment.objects.filter(poolroom=poolroom.id)
    json_serializer = serializers.get_serializer("json")()
    response = HttpResponse()
    response['Cache-Control'] = 'max-age=%s' % (60 * 60 * 24 * 7)
    json_serializer.serialize(equipments, fields=('tabletype', 'producer', 'quantity', 'cue', 'price'), ensure_ascii=False, stream=response, indent=2, use_natural_keys=True)
    return response
        
def nearby(request, lat = None, lng = None):
    if lat is not None and lng is not None:
        '''
        radius distance
        https://developers.google.com/maps/articles/phpsqlsearch_v3?csw=1#findnearsql
        '''
        haversine = '6371 * acos( cos( radians(%s) ) * cos( radians( lat ) ) * cos( radians( lng ) - radians(%s) ) + sin( radians(%s) ) * sin( radians( lat ) ) )' %(lat, lng, lat)
        nearby_poolrooms = Poolroom.objects.extra(select={'distance' : haversine}).extra(order_by=['distance'])\
            .extra(where=["1 having distance <= 10"])#[:5]
        # hacking
        concrete_model = nearby_poolrooms[0]._meta.concrete_model
        distance = models.DecimalField(name='distance', max_digits=11,decimal_places=7,null=True)
        setattr(distance, 'attname', 'distance')
        concrete_model._meta.local_fields.append(distance)
        json_serializer = serializers.get_serializer("json")()
        response = HttpResponse()
        json_serializer.serialize(nearby_poolrooms, ensure_ascii=False, stream=response, indent=2, use_natural_keys=True)
        return response
    return render_to_response(TEMPLATE_ROOT + 'poolroom_nearby.html', {},
                              context_instance=RequestContext(request))
    
def detail(request, poolroomid):
    poolroom = get_object_or_404(Poolroom, pk=poolroomid)
    return HttpResponse()