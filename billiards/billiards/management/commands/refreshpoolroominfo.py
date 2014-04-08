# -*- coding: utf-8 -*-
# encoding: utf-8
'''
@author: kane
A utility tool to create test data from product db.
'''
from django.core.management.base import NoArgsCommand
import billiards
import os
from billiards.models import Poolroom
from django.db.models.query_utils import Q
import requests
from billiards.citydistrict import CITY_DISTRICT

class Command(NoArgsCommand):
    help = 'Refresh poolroom\'s location ifo'
    apppath = os.path.abspath(billiards.__path__[0])

    geocoderURL = "http://api.map.baidu.com/geocoder/v2/?ak=%s&location=%s,%s&output=json&pois=0"
    ak = "lzLVWuWXTWRpmUq78cD5CEwE"
    
    def handle(self, *args, **options):
        poolrooms = Poolroom.objects.filter(Q(district__isnull=True) | Q(district='') | Q(city=0))
        for poolroom in poolrooms:
            url = self.geocoderURL %(self.ak, poolroom.lat_baidu, poolroom.lng_baidu)
            r = requests.get(url)
            if r.status_code == 200:
                geojson = r.json()
                poolroom.city = CITY_DISTRICT.get(geojson['result']['addressComponent']['city'])[0]
                poolroom.district = geojson['result']['addressComponent']['district']
                poolroom.save()
                self.stdout.write('Successfully update \'%s\' as %s %s.\n' %(poolroom.name, poolroom.get_city_display(), 
                                                                             poolroom.district))