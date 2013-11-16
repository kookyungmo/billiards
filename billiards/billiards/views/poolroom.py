# -*- coding: utf-8 -*-
# encoding: utf-8
'''

@author: kane
'''

from django.http import HttpResponse
from billiards.models import Poolroom, PoolroomEquipment
from django.shortcuts import get_object_or_404
from django.core import serializers

def more(request, poolroomid):
    poolroom = get_object_or_404(Poolroom, pk=poolroomid)

    equipments = PoolroomEquipment.objects.filter(poolroom=poolroom.id)
    json_serializer = serializers.get_serializer("json")()
    response = HttpResponse()
    response['Cache-Control'] = 'max-age=%s' % (60 * 60 * 24 * 7)
    json_serializer.serialize(equipments, fields=('tabletype', 'producer', 'quantity', 'cue', 'price'), ensure_ascii=False, stream=response, indent=2, use_natural_keys=True)
    return response