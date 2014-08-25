# -*- coding: utf-8 -*-
# encoding: utf-8
'''

@author: kane
'''

from django.http import HttpResponse, Http404
from billiards.models import Poolroom, PoolroomEquipment, poolroom_fields, Match,\
    poolroomimage_fields, Coupon, poolroomcoupon_fields, getCouponCriteria
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.core import serializers
from django.template.context import RequestContext
from billiards.settings import TEMPLATE_ROOT
from billiards.location_convertor import bd2gcj, gcj2bd
from django.db.models.query_utils import Q
import datetime
from dateutil.relativedelta import relativedelta
from StringIO import StringIO
from django.utils import simplejson
from billiards.views.match import tojson
from django.utils.timezone import utc
from billiards.annotation import deprecated
import uuid
import operator
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import urlunquote_plus
from billiards.commons import num

def more_uuid(request, poolroom_uuid):
    uuidobj = uuid.UUID(poolroom_uuid)
    poolroom = getPoolroomByUUID(uuidobj)

    equipments = PoolroomEquipment.objects.filter(poolroom=poolroom.id)
    json_serializer = serializers.get_serializer("json")()
    response = HttpResponse()
    response['Cache-Control'] = 'max-age=%s' % (60 * 60 * 24 * 7)
    json_serializer.serialize(equipments, fields=('tabletype', 'producer', 'quantity', 'cue', 'price'), ensure_ascii=False, stream=response, indent=2, use_natural_keys=True)
    return response
    
def more(request, poolroomid):
    poolroom = getPoolroom(poolroomid)
    return redirect('poolroom_moreinfo_uuid', poolroom_uuid=str(poolroom.uuid))

def updateJsonStrWithDistance(poolroomJsonStr, poolrooms):        
    poolroomObjs = simplejson.loads(poolroomJsonStr)
    for poolroomObj in poolroomObjs:
        for poolroom in poolrooms:
            if poolroom.id == poolroomObj['pk']:
                poolroomObj['fields']['distance'] = str(poolroom.location_distance.km)
                break
    return simplejson.dumps(poolroomObjs)

def updateJsonStrWithImages(poolroomJsonStr, poolrooms):        
    poolroomObjs = simplejson.loads(poolroomJsonStr)
    for poolroomObj in poolroomObjs:
        for poolroom in poolrooms:
            if poolroom.id == poolroomObj['pk']:
                images = {}
                for i, image in enumerate(poolroom.images):
                    images['img' + str(i)] = simplejson.loads(tojson(image, poolroomimage_fields)[1:-1])
                poolroomObj['fields']['images'] = images
                break
    return simplejson.dumps(poolroomObjs)

def updateJsonStrWithCoupons(poolroomJsonStr, poolrooms):        
    poolroomObjs = simplejson.loads(poolroomJsonStr)
    for poolroomObj in poolroomObjs:
        for poolroom in poolrooms:
            if poolroom.id == poolroomObj['pk']:
                coupons = {}
                for i, coupon in enumerate(poolroom.coupons[:2]):
                    coupons['coupon' + str(i)] = simplejson.loads(tojson(coupon, poolroomcoupon_fields)[1:-1])
                poolroomObj['fields']['coupons'] = coupons
                break
    return simplejson.dumps(poolroomObjs)
    
def getNearbyPoolrooms(lat, lng, distance, where = None):
    googles = bd2gcj(float(lat), float(lng))
    '''
    radius distance
    https://developers.google.com/maps/articles/phpsqlsearch_v3?csw=1#findnearsql
    '''
    qs = Poolroom.objects.filter(Q(exist=1))
    if where is not None:
        qs = qs.extra(where=[where])
    if distance is not None:
        qs = qs.filter(location__distance_lt=((googles[0], googles[1]), num(distance))).order_by_distance()
    else:
        qs = qs.order_by_distance_from(location=(googles[0], googles[1]), field_name='location')
    return qs

def toJson(queryset, fields):
    json_serializer = serializers.get_serializer("json")()
    stream = StringIO()
    json_serializer.serialize(queryset, fields=fields, ensure_ascii=False, stream=stream, indent=2, use_natural_keys=True)
    jsonstr = stream.getvalue()
    return jsonstr
    
def nearby(request, lat = None, lng = None, distance = 10):
    if lat is not None and lng is not None:
        nearby_poolrooms = getNearbyPoolrooms(lat, lng, distance)
        jsonstr = toJson(nearby_poolrooms, poolroom_fields)
        if len(nearby_poolrooms) > 0:
            jsonstr = updateJsonStrWithDistance(jsonstr, nearby_poolrooms)
            jsonstr = updateJsonStrWithImages(jsonstr, nearby_poolrooms)
            jsonstr = updateJsonStrWithCoupons(jsonstr, nearby_poolrooms)
        return HttpResponse(jsonstr)
    return render_to_response(TEMPLATE_ROOT + 'poolroom_nearby.html', {'defaultDistance': 5},
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

def getCoupons(poolroomid):
    return Coupon.objects.filter(getCouponCriteria() & Q(poolroom__id=poolroomid)).order_by('-discount')
    
def isGracePeriod():
    return datetime.datetime.strptime('Sep 1 2014', '%b %d %Y').replace(tzinfo=utc) - datetime.datetime.utcnow().replace(tzinfo=utc) > datetime.timedelta(seconds = 5) 

@deprecated
def getPoolroom(poolroomid):
    if isGracePeriod():
        return get_object_or_404(Poolroom, pk=poolroomid, exist=1)
    raise Http404()

def getPoolroomByUUID(uuid):
    return get_object_or_404(Poolroom, uuid=uuid, exist=1)
    
def detail_uuid(request, poolroom_uuid):
    uuidobj = uuid.UUID(poolroom_uuid)
    poolroom = getPoolroomByUUID(uuidobj)
    
    starttime = datetime.datetime.today()
    endtime = starttime + relativedelta(days=30)
    datefmt = "%Y-%m-%d"
    matches = Match.objects.filter(Q(starttime__gte=starttime.strftime(datefmt)) & Q(poolroom__uuid=uuidobj)) \
        .exclude(starttime__gt=endtime.strftime(datefmt)).order_by('starttime')
        
    equipments = PoolroomEquipment.objects.filter(poolroom=poolroom.id)

    return render_to_response(TEMPLATE_ROOT + 'poolroom_detail.html', 
                              {'poolroom': poolroom, 'matches':matches, 'equipments': equipments},
                              context_instance=RequestContext(request))
    
def detail(request, poolroomid):
    poolroom = getPoolroom(poolroomid)
    
    return redirect('poolroom_detail_uuid', poolroom_uuid=str(poolroom.uuid))

@csrf_exempt
def query(request, keyword):
    decodedKeyword = urlunquote_plus(keyword)
    rt = Poolroom.objects.filter(reduce(operator.and_, (Q(name__contains=kw) for kw in decodedKeyword.strip().split(' '))) & Q(exist=1)).order_by('-rating')[:10]
    return HttpResponse(toJson(rt, poolroom_fields))