# -*- coding: utf-8 -*-
# encoding: utf-8
import datetime
import hashlib
import uuid

from django.core.exceptions import PermissionDenied
from django.db.models.aggregates import Max, Min
from django.db.models.query_utils import Q
from django.http.response import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template.context import RequestContext
from django.utils import simplejson
from django.utils.timezone import pytz, utc
from django.views.decorators.csrf import csrf_exempt
from mobi.decorators import detect_mobile

from billiards.commons import tojson2, NoObjectJSONSerializer, json_serial,\
    forceLogin, isWechatBrowser
from billiards.models import Assistant, AssistantOffer, Poolroom, \
    assistant_fields, AssistantImage, \
    assistantimage_fields, assistantoffer_fields_2, AssistantAppointment, Goods,\
    assistant_appointment_fields, AssistantLikeStats, AssistantUser
from billiards.settings import TEMPLATE_ROOT
from billiards.views.transaction import createTransaction, PAYMENT_TIMEOUT
from billiards import settings
import json
from datetime import timedelta
from django.core.cache import cache
from random import randint

def assistant(request):
    return render_to_response(TEMPLATE_ROOT + 'escort/list.html', context_instance=RequestContext(request))
    
class AssistantJSONSerializer(NoObjectJSONSerializer):
    def handle_field(self, obj, field):
        if field.name == 'poolroom':
            value = field._get_val_from_obj(obj)
            if value is not None:
                self._current[field.name] = Poolroom.objects.get(id=value).natural_key_simple()
            else:
                self._current[field.name] = '{}';
        elif field.name == 'chargeCode':
            if obj.state == 1 or obj.state == 4 or obj.state == 8:
                self._current[field.name] = 'Paid First'
            else:
                super(AssistantJSONSerializer, self).handle_field(obj, field)
        else:
            super(AssistantJSONSerializer, self).handle_field(obj, field)
            
    def handle_fk_field(self, obj, field):
        if field.name == 'user':
            self._current[field.name] = {'name': u"%s" %(getattr(obj, field.name))}
        else:
            NoObjectJSONSerializer.handle_fk_field(self, obj, field)
            
class AssistantOrdersJSONSerializer(AssistantJSONSerializer):
    def handle_fk_field(self, obj, field):
        if field.name == 'transaction':
            self._current[field.name] = field._get_val_from_obj(obj)
        else:
            AssistantJSONSerializer.handle_fk_field(self, obj, field)
            
def updateOffers(offers):
    for offer in offers:
        assistant = Assistant.objects.get(id=offer['assistant'])
        offer['assistant'] = assistant.natural_key()
        offer['offers'] = getOffers(offer['assistant']['uuid'])
        offer['pageview'] = getPageView(assistant, 0)
    return offers

ASSISTANT_FILTER = Q(state=1)
ASSISTANT_OFFER_FILTER = Q(status=1)
ASSISTANT_IMAGE_FILTER = Q(status=1)
ASSISTANTAPPOINTMENT_FILTER = ~Q(state=8) & ~Q(state=16)
def assistant_list(request):
    # really tricky
    assistantsOffers = AssistantOffer.objects.values('assistant').filter(ASSISTANT_OFFER_FILTER).filter(assistant__in=Assistant.objects.filter(ASSISTANT_FILTER))\
        .annotate(maxprice = Max('price'), minprice = Min('price'), poolroom = Min('poolroom'))
    jsonstr = json.dumps(list(updateOffers(assistantsOffers)), default=json_serial)
    return HttpResponse(jsonstr)

@csrf_exempt
def user_assistant_order(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            appoints = AssistantAppointment.objects.filter(user=request.user).order_by("-createdDate")
            for appoint in appoints:
                if appoint.transaction.state == 2 or appoint.transaction.state == 5:
                    if appoint.state == 1:
                        appoint.state = 2
                        appoint.save()
                elif appoint.transaction.state != 3 and appoint.transaction.paymentExpired:
                    appoint.transaction.state = 3
                    appoint.transaction.save()
                    appoint.state = 8
                    appoint.save()
            return HttpResponse(tojson2(appoints, AssistantJSONSerializer(), assistant_appointment_fields + ('transaction', 'chargeCode', )))
        else:
            return render_to_response(TEMPLATE_ROOT + 'escort/order.html', context_instance=RequestContext(request))
    return redirect('assistant_list')

@csrf_exempt
def assistant_by_uuid(request, assistant_uuid):
    if request.method == 'GET':
        assistant = get_object_or_404(Assistant, uuid=uuid.UUID(assistant_uuid))
        return render_to_response(TEMPLATE_ROOT + 'escort/detail.html', {'as': assistant}, 
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        try:
            assistant = Assistant.objects.get(uuid=uuid.UUID(assistant_uuid))
            assistantobj = simplejson.loads(tojson2(assistant, AssistantJSONSerializer(), assistant_fields))
            assistantobj[0]['images'] = simplejson.loads(tojson2(AssistantImage.objects.filter(assistant=assistant).filter(ASSISTANT_IMAGE_FILTER), 
                                                                 AssistantJSONSerializer(), assistantimage_fields))
            return HttpResponse(simplejson.dumps(assistantobj))
        except Assistant.DoesNotExist:
            return HttpResponse("{'error': 'not found', 'code': 0}")

def getOffers(assistant_uuid):
    offers = {}
    weekday = datetime.datetime.today().weekday()
    weekdays = [(weekday + i) % 7 for i in range(3)]
    for idx, weekday in enumerate(weekdays):
        assistantsOffers = AssistantOffer.objects.filter(ASSISTANT_OFFER_FILTER).filter(
            assistant=Assistant.objects.filter(ASSISTANT_FILTER).get(uuid=uuid.UUID(assistant_uuid))).filter(day=getattr(AssistantOffer.day, AssistantOffer.day._flags[weekday]))
        offers[idx] = simplejson.loads(tojson2(assistantsOffers, AssistantJSONSerializer(), assistantoffer_fields_2))
    return offers 
        
@csrf_exempt
def assistant_offer_by_uuid(request, assistant_uuid):
    try:
        return HttpResponse(simplejson.dumps([getOffers(assistant_uuid)]))
    except Assistant.DoesNotExist:
        return HttpResponse("{'error': 'not found', 'code': 0}")
    
@csrf_exempt
@detect_mobile
def assistant_offer_booking_by_uuid(request, assistant_uuid):
    if request.user.is_authenticated():
        if request.user.cellphone is None or request.user.cellphone == '':
            return HttpResponse(simplejson.dumps({'code': 16, 'msg': 'missing contact information'}))
        try:
            offer_booking = simplejson.loads(request.body)
            offerday = datetime.datetime.utcfromtimestamp(float(offer_booking['offerDay'])).replace(tzinfo=utc).astimezone(pytz.timezone(settings.TIME_ZONE))
            if (offerday - datetime.datetime.now().replace(tzinfo=utc)).days <= 2:
                offerhour = int(offer_booking['offerHour'])
                offerday = offerday.replace(hour=offerhour, minute=0)
                offerduring = int(offer_booking['offerDuring'])
                assistant = Assistant.objects.filter(ASSISTANT_FILTER).get(uuid=uuid.UUID(assistant_uuid))
                assistantsOffers = AssistantOffer.objects.filter(ASSISTANT_OFFER_FILTER).filter(
                   assistant=assistant).filter(day=getattr(AssistantOffer.day, AssistantOffer.day._flags[offerday.weekday()]))
                offertimerange = [offerday, offerday + datetime.timedelta(hours=offerduring)]
                for offer in assistantsOffers:
                    if offer.starttime.hour <= offerhour and offer.endtime.hour > offerhour and offer.endtime.hour >= (offerhour + offerduring):
                        appoints = AssistantAppointment.objects.filter(ASSISTANTAPPOINTMENT_FILTER).filter(assistant=assistant).filter(
                            (Q(starttime__gte=offertimerange[0]) & Q(starttime__lt=offertimerange[1])) | 
                            (Q(endtime__gt=offertimerange[0]) & Q(endtime__lte=offertimerange[1])))
                        if appoints.exists():
                            available_payment = True
                            for appoint in appoints:
                                if (appoint.transaction.state == 2 or appoint.transaction.state == 5) or \
                                    (appoint.transaction.state == 1 and not appoint.transaction.paymentExpired):
                                    if appoint.user == request.user:
                                        return HttpResponse(simplejson.dumps({'code': 2, 'msg': 'order has been created', 'state': appoint.state}))
                                    else:
                                        available_payment = False
                                else:
                                    appoint.state = 8
                                    appoint.transaction.state = 3
                                    appoint.transaction.save()
                                    appoint.save()
                            if not available_payment:
                                return HttpResponse(simplejson.dumps({'code': 1, 'msg': 'unavailable'}))
                        # retrieve/create a goods
                        name = u"预约%s %s点 至 %s点" %(offer.assistant.nickname, offertimerange[0].strftime("%Y-%m-%d %H"), offertimerange[1].strftime("%H"))
                        hashvalue = hashlib.md5(u"%s %s-%s" %(offer.assistant.uuid, offertimerange[0], offertimerange[1])).hexdigest().upper()
                        goods, created = Goods.objects.get_or_create(sku=hashvalue, defaults={'name': name, 'description': name, 'price':offer.price*offerduring,
#                        goods, created = Goods.objects.get_or_create(sku=hashvalue, defaults={'name': name, 'description': name, 'price':0.01,  
                                    'type': 2, 'sku': hashvalue})
                        transaction, url = createTransaction(request, goods)
                        transaction.validUntilDate = datetime.datetime.now() + timedelta(minutes=PAYMENT_TIMEOUT)
                        transaction.save()
                        AssistantAppointment.objects.create(assistant=assistant, user=request.user, poolroom=offer.poolroom, 
                                    goods=goods, transaction=transaction, starttime=offertimerange[0], endtime=offertimerange[1],
                                    duration=offerduring, price=goods.price, createdDate=datetime.datetime.now(), state=1)
                        return HttpResponse(simplejson.dumps({'code': 0, 'msg': 'order is created.', 'payurl': url}))
                return HttpResponse(simplejson.dumps({'code': -3, 'msg': 'illegal data'}))
            return HttpResponse(simplejson.dumps({'code': -2, 'msg': 'illegal day'}))
        except Assistant.DoesNotExist:
            return HttpResponse(simplejson.dumps({'code': -1, 'msg': 'illegal data'}))
        except ValueError:
            return HttpResponse(simplejson.dumps({'code': -1, 'msg': 'illegal data'}))
    
    raise PermissionDenied("login firstly.")

@csrf_exempt
def assistant_like_by_uuid(request, assistant_uuid):
    if request.user.is_authenticated():
        try:
            assistant = Assistant.objects.filter(ASSISTANT_FILTER).get(uuid=uuid.UUID(assistant_uuid))
            likeStat, created = AssistantLikeStats.objects.get_or_create(assistant=assistant, user=request.user,
                    defaults={'assistant': assistant, 'user': request.user, 'lastUpdated': datetime.datetime.now()})
            if created:
                updateAssistantLike(assistant, 1)
                return HttpResponse(simplejson.dumps({'code': 0, 'msg': 'liked'}))
            elif not likeStat.isLiked:
                likeStat.isLiked = True
                likeStat.lastUpdated = datetime.datetime.now()
                likeStat.save()
                return HttpResponse(simplejson.dumps({'code': 0, 'msg': 'reliked'}))
            else:
                return HttpResponse(simplejson.dumps({'code': 0, 'msg': 'already liked'}))
        except Assistant.DoesNotExist:
            return HttpResponse(simplejson.dumps({'code': -1, 'msg': 'illegal data'}))
    raise PermissionDenied("login firstly.")

@csrf_exempt
def assistant_unlike_by_uuid(request, assistant_uuid):
    if request.user.is_authenticated():
        try:
            assistant = Assistant.objects.filter(ASSISTANT_FILTER).get(uuid=uuid.UUID(assistant_uuid))
            likeStat = AssistantLikeStats.objects.get(assistant=assistant, user=request.user)
            if likeStat.isLiked:
                likeStat.isLiked = False
                likeStat.lastUpdated = datetime.datetime.now()
                likeStat.save()
                updateAssistantLike(assistant, -1)
                return HttpResponse(simplejson.dumps({'code': 0, 'msg': 'unliked'}))
            else:
                return HttpResponse(simplejson.dumps({'code': 0, 'msg': 'already unliked'}))
        except AssistantLikeStats.DoesNotExist:
            return HttpResponse(simplejson.dumps({'code': -2, 'msg': 'illegal request'}))
        except Assistant.DoesNotExist:
            return HttpResponse(simplejson.dumps({'code': -1, 'msg': 'illegal data'}))
    raise PermissionDenied("login firstly.")

TIMEOUT = 60 * 60 * 24 * 2
def updateAssistantLike(assistant, delta):
    likes = cache.get(ASSISTANT_LIKE %(str(assistant.uuid)))
    if likes == None:
        likes = AssistantLikeStats.objects.filter(Q(assistant=assistant) & Q(isLiked=True)).count()
    if delta != 0:
        cache.set(ASSISTANT_LIKE %(assistant.uuidstr), likes + delta, TIMEOUT)
    return likes + delta

def getPageView(assistant, delta = 1):
    assistant_uuid = str(assistant.uuid)
    pageView = cache.get(ASSISTANT_PAGEVIEW %(assistant_uuid))
    if pageView == None:
        pageView = assistant.pageview
        if delta != 0:
            pageView += delta
            cache.set(ASSISTANT_PAGEVIEW %(assistant_uuid), pageView, None)
    else:
        if delta != 0:
            pageView += delta
            if pageView % 100 == 0:
                assistant.pageview = pageView
                assistant.save()
            cache.set(ASSISTANT_PAGEVIEW %(assistant_uuid), pageView, None)
    return pageView

ASSISTANT_PAGEVIEW = "%s_pageview"
ASSISTANT_LIKE = "%s_like"
def assistant_stats_by_uuid(request, assistant_uuid):
    try:
        assistant = Assistant.objects.filter(ASSISTANT_FILTER).get(uuid=uuid.UUID(assistant_uuid))
        pageView = getPageView(assistant, randint(1, 6))
        return HttpResponse(simplejson.dumps({'code': 0, 'likes': updateAssistantLike(assistant, 0), 'pageview': pageView}))
    except Assistant.DoesNotExist:
        return HttpResponse(simplejson.dumps({'code': -1, 'msg': 'illegal data'}))
    
@csrf_exempt
def assistant_orders_by_uuid(request, assistant_uuid):
    if request.user.is_authenticated():
        try:
            assistant = Assistant.objects.filter(ASSISTANT_FILTER).get(uuid=uuid.UUID(assistant_uuid))
            aUser = AssistantUser.objects.filter(Q(user=request.user)).get(assistant=assistant)
            if request.method == 'POST':
                appoints = AssistantAppointment.objects.filter(Q(assistant=assistant)).filter(
                    Q(state=2) | Q(state=4) | Q(state=32) | Q(state=256)).order_by("-createdDate")
                return HttpResponse(tojson2(appoints, AssistantOrdersJSONSerializer(), assistant_appointment_fields + ('user', 'transaction',)))
            else:
                return render_to_response(TEMPLATE_ROOT + 'escort/asorder.html', {'as': assistant}, context_instance=RequestContext(request))
        except Assistant.DoesNotExist:
            raise Http404("illegal access.")
        except AssistantUser.DoesNotExist:
            raise PermissionDenied("illegal access.")
    if isWechatBrowser(request.META['HTTP_USER_AGENT']):
        return forceLogin(request, 'wechat')
    raise PermissionDenied("login firstly.")

@csrf_exempt
def assistant_order_complete_by_tid(request, assistant_uuid, transaction_id):
    if request.user.is_authenticated():
        try:
            assistant = Assistant.objects.filter(ASSISTANT_FILTER).get(uuid=uuid.UUID(assistant_uuid))
            aUser = AssistantUser.objects.filter(Q(user=request.user)).get(assistant=assistant)
            appoint = AssistantAppointment.objects.get(assistant=assistant, transaction=transaction_id)
            orderCode = simplejson.loads(request.body)
            if appoint.state == 32:
                if appoint.chargeCode.lower() == orderCode['code'].strip().lower() and \
                    (appoint.transaction.state == 2 or appoint.transaction.state == 5):
                    appoint.state = 256
                    appoint.save()
                    return HttpResponse(simplejson.dumps({'code': 0, 'msg': 'Completed.'}))
                return HttpResponse(simplejson.dumps({'code': -2, 'msg': 'Mismatched charged code.'}))
            elif appoint.state == 256:
                return HttpResponse(simplejson.dumps({'code': 1, 'msg': 'Already completed.'}))
            else:
                return HttpResponse(simplejson.dumps({'code': -3, 'msg': 'Illegal request.'}))
        except Assistant.DoesNotExist:
            raise Http404("illegal access.")
        except AssistantUser.DoesNotExist:
            raise PermissionDenied("illegal access.")
        except ValueError:
            return HttpResponse(simplejson.dumps({'code': -1, 'msg': 'illegal data'}))

    raise PermissionDenied("login firstly.")
