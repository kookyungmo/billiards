# -*- coding: utf-8 -*-
# encoding: utf-8
'''
@author: kane
A utility tool to create test data from product db.
'''
from django.core import serializers
from django.db.models.query_utils import Q
from billiards.models import Poolroom, Match, Group, Coupon, PoolroomImage,\
    Event
from django.core.management.base import NoArgsCommand
import billiards
import os
from itertools import chain

class Command(NoArgsCommand):
    help = 'Dump data of product db to fixtures for testing'
    apppath = os.path.abspath(billiards.__path__[0])

    def handle(self, *args, **options):
        poolroomTestDataQuery = Poolroom.objects.filter(Q(id=137) | Q(id=148) | Q(id=15) | Q(id=20) | Q(id=187))
        poolroomImagesTestDataQuery = PoolroomImage.objects.filter(poolroom=15)
        data = serializers.serialize("json", chain(poolroomTestDataQuery, poolroomImagesTestDataQuery), indent=4)
        out = open("%s/fixtures/poolroom.json" %(self.apppath), "w")
        out.write(data)
        out.close()
        
        matchTestDataQuery = Match.objects.filter(Q(id__gte=81) & Q(id__lte=84))
        data = serializers.serialize("json", matchTestDataQuery, indent=4)
        out = open("%s/fixtures/match.json" %(self.apppath), "w")
        out.write(data)
        out.close()
        
        groupTestDataQuery = Group.objects.all()
        data = serializers.serialize("json", groupTestDataQuery, indent=4)
        out = open("%s/fixtures/group.json" %(self.apppath), "w")
        out.write(data)
        out.close()
        
        couponTestDataQuery = Coupon.objects.filter(Q(poolroom=137) | Q(poolroom=187))
        data = serializers.serialize("json", couponTestDataQuery, indent=4)
        out = open("%s/fixtures/coupon.json" %(self.apppath), "w")
        out.write(data)
        out.close()
        
        eventTestDataQuery = Event.objects.filter(Q(id__lte=2))
        data = serializers.serialize("json", eventTestDataQuery, indent=4)
        out = open("%s/fixtures/event.json" %(self.apppath), "w")
        out.write(data)
        out.close()
