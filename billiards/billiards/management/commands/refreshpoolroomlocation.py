# -*- coding: utf-8 -*-
# encoding: utf-8
'''
@author: kane
A utility tool to create test data from product db.
'''
from django.core.management.base import NoArgsCommand
from billiards.models import Poolroom

class Command(NoArgsCommand):
    help = 'Refresh poolroom\'s location'
    
    def handle(self, *args, **options):
        poolrooms = Poolroom.objects.all()
        self.stdout.write('Found %s poolrooms.\n' %(len(poolrooms)))
        for poolroom in poolrooms:
            if poolroom.location is None or poolroom.location == '':
                poolroom.location = (poolroom.lat, poolroom.lng)
                poolroom.save()
                self.stdout.write('Successfully update \'%s\' as %s.\n' %(poolroom.name, poolroom.location))