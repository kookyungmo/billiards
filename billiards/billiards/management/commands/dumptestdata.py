# -*- coding: utf-8 -*-
# encoding: utf-8
'''
@author: kane
A utility tool to create test data from product db.
'''
from django.core import serializers
from django.db.models.query_utils import Q
from billiards.models import Poolroom, Match, Group, Coupon, PoolroomImage,\
    Event, Assistant, AssistantUser, AssistantOffer, AssistantImage
from django.core.management.base import NoArgsCommand
import billiards
import os
from itertools import chain
from django.contrib.auth.models import User
from django.core.serializers.json import Serializer
from bitfield.models import BitField
from django.utils.encoding import is_protected_type
            
class ExportSerializer(Serializer): 

    def handle_field(self, obj, field): 
        value = field._get_val_from_obj(obj) 

        #If the object has a get_field_display() method, use it. 
        display_method = "get_%s_display" % field.name 
        if  hasattr(field, 'export_use_value') and getattr(field, 'export_use_value')() == True:
            if isinstance(field, BitField):
                self._current[field.name] = int(value)
            else:
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

        userQuery = User.objects.filter(username=u'075F3CE411F54B563EDAADC829E86')
        assistantQuery = Assistant.objects.all()
        auQuery = AssistantUser.objects.all()
        export_serializer = ExportSerializer()
        data = export_serializer.serialize(chain(userQuery, assistantQuery, auQuery), indent=4)
        out = open("%s/fixtures/assistantuser.json" %(self.apppath), "w")
        out.write(data)
        out.close()
        
        data = export_serializer.serialize(chain(Assistant.objects.all(), AssistantOffer.objects.all(), AssistantImage.objects.all()), indent = 4)
        out = open("%s/fixtures/assistants.json" %(self.apppath), "w")
        out.write(data)
        out.close()