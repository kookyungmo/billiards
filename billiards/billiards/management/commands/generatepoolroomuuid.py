# -*- coding: utf-8 -*-
# encoding: utf-8
'''
@author: kane
A utility tool to generate UUID for poolroom
'''
from django.core.management.base import NoArgsCommand
from billiards.models import Poolroom
from django.db.models.query_utils import Q
from uuidfield.fields import UUIDField
    
class Command(NoArgsCommand):
    help = 'Generate UUID for poolroom'
    
    def handle(self, *args, **options):
        poolrooms = Poolroom.objects.filter(Q(uuid__isnull=True) | Q(uuid=''))
        for poolroom in poolrooms:
            self.stdout.write('Generating UUID for poolroom "%s".\n' %(poolroom.name))
            poolroom.uuid = UUIDField(hyphenate=True)._create_uuid()
            poolroom.save()
            self.stdout.write('New UUID for poolroom "%s" is "%s".\n' %(poolroom.name, poolroom.uuid))
                            