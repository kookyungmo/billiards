# -*- coding: utf-8 -*-
# encoding: utf-8
'''

@author: kane
'''

from django.http import HttpResponse, Http404
from billiards.models import Poolroom, PoolroomEquipment, poolroom_fields
from django.shortcuts import get_object_or_404, render_to_response
from django.core import serializers
from django.template.context import RequestContext
from billiards.settings import TEMPLATE_ROOT
from django.db import models
from billiards.location_convertor import bd2gcj, gcj2bd
from django.db.models.query_utils import Q

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
        googles = bd2gcj(float(lat), float(lng))
        '''
        radius distance
        https://developers.google.com/maps/articles/phpsqlsearch_v3?csw=1#findnearsql
        '''
        haversine = '6371 * acos( cos( radians(%s) ) * cos( radians( lat ) ) * cos( radians( lng ) - radians(%s) ) + sin( radians(%s) )\
             * sin( radians( lat ) ) )' %(googles[0], googles[1], googles[0])
        nearby_poolrooms = Poolroom.objects.extra(select={'distance' : haversine}).extra(order_by=['distance'])\
            .extra(where=["1 having distance <= 10"])#[:5]
        # hacking
        concrete_model = nearby_poolrooms[0]._meta.concrete_model
        distance = models.DecimalField(name='distance', max_digits=11,decimal_places=7,null=True)
        setattr(distance, 'attname', 'distance')
        concrete_model._meta.local_fields.append(distance)
        json_serializer = serializers.get_serializer("json")()
        response = HttpResponse()
        fields = list(poolroom_fields)
        fields.append('distance')
        json_serializer.serialize(nearby_poolrooms, fields=fields, ensure_ascii=False, stream=response, indent=2, use_natural_keys=True)
        return response
    return render_to_response(TEMPLATE_ROOT + 'poolroom_nearby.html', {},
                              context_instance=RequestContext(request))
    
def updateBaiduLocation(request):
    if request.user.is_authenticated() and request.user.is_superuser:
        withoutBaiduLocation = None
        try:
            if (request.GET.get['all'] is not None):
                withoutBaiduLocation = Poolroom.objects.all()
        except Exception:
            if withoutBaiduLocation is None:
                withoutBaiduLocation = Poolroom.objects.filter(Q(lat_baidu__exact=0) | Q(lng_baidu__exact=0))
        for poolroom in withoutBaiduLocation:
            baiduLoc = gcj2bd(float(poolroom.lat), float(poolroom.lng))
            poolroom.lat_baidu = baiduLoc[0]
            poolroom.lng_baidu = baiduLoc[1]
            poolroom.save()
        return HttpResponse("[{'msg':'%s records updated.'}]" %(withoutBaiduLocation.count()))
    else:
        raise Http404()
    
def detail(request, poolroomid):
    poolroom = get_object_or_404(Poolroom, pk=poolroomid)
    return HttpResponse()
