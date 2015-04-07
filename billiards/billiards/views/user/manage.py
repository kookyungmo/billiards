# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2014年1月1日

@author: kane
'''
from django.http import HttpResponse
from billiards.models import Group, Membership
from django.db.models.query_utils import Q
from billiards.settings import TEMPLATE_ROOT, PREFER_LOGIN_SITE,\
    SOCIALOAUTH_SITES, STATIC_URL
from django.template.context import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
import json
from billiards.commons import forceLogin
from django.utils import simplejson
from django.core.exceptions import PermissionDenied
import re
from validate_email import validate_email
from rest_framework.response import Response
from rest_framework_jsonp.renderers import JSONPRenderer
from rest_framework.decorators import api_view, renderer_classes
from django.contrib import auth
from billiards.views.user.login import login_3rd_page

PHONE_PATTERN = re.compile(r'^1\d{10}$')    
@csrf_exempt
def completeInfo(request):
    user = request.user
    if user.is_authenticated():
        contactInfo = simplejson.loads(request.body)
        if str(contactInfo['tel']).strip() != '' and PHONE_PATTERN.search(str(contactInfo['tel']).strip()) and validate_email(contactInfo['email']):
            user.cellphone = str(contactInfo['tel']).strip()
            user.email = str(contactInfo['email']).strip()
            user.save()
            return HttpResponse(simplejson.dumps({'code': 0}))
        return HttpResponse(simplejson.dumps({'code': -1}))
    raise PermissionDenied("login firstly.")    

MEMBERSHIP_PAGE = 'user/membership.html'
@csrf_exempt
def membership_apply(request, wechatid, group):
    if request.user.is_authenticated() and request.user.site_name.startswith(PREFER_LOGIN_SITE):
        groupobj = get_object_or_404(Group, id=group)
        if request.method == 'POST':
            realname = request.POST['realname']
            cellphone = request.POST['cellphone']
            gender = request.POST['gender']
            obj, created = Membership.objects.get_or_create(wechatid=wechatid, targetid_id=group,
                          defaults={'userid': request.user.id if request.user.is_authenticated() else 0,
                                    'name': realname, 'gender': int(gender), 'cellphone': cellphone})
            if obj != None:
                return HttpResponse(json.dumps({'rt': 1, 'msg': 'created'}), content_type="application/json")
            else:
                return HttpResponse(json.dumps({'rt': 0, 'msg': 'failed to apply a membership'}), content_type="application/json")
        try:
            member = Membership.objects.get(Q(wechatid=wechatid) & Q(targetid=group))
            return renderMemberPage(request, member, groupobj)
        except Membership.DoesNotExist:
            return render_to_response(TEMPLATE_ROOT + 'user/membership_application.html',
                    {'group': groupobj, 'wechatid': wechatid}, context_instance=RequestContext(request))

    return forceLogin(request, PREFER_LOGIN_SITE)
def renderMemberPage(request, member, groupobj):
    return render_to_response(TEMPLATE_ROOT + MEMBERSHIP_PAGE,
            {'group': groupobj, 'member': member}, context_instance=RequestContext(request))

def membership(request, wechatid, group):
    groupobj = get_object_or_404(Group, id=group)
    try:
        member = Membership.objects.get(Q(wechatid=wechatid) & Q(targetid=group))
        return renderMemberPage(request, member, groupobj)
    except Membership.DoesNotExist:
        return redirect('membership_apply', wechatid=wechatid, group=group)

def sign_request(raw, key):
    from hashlib import sha1
    import hmac
    hashed = hmac.new(key, raw, sha1)
    # The signature
    return hashed.digest().encode("base64").rstrip('\n')

@api_view(['GET'])
@renderer_classes((JSONPRenderer,))
def sohucs_getinfo(request):
    if request.user.is_authenticated():
        strToBeSigned = u'img_url=%s&nickname=%s&profile_url=%s&user_id=%s' %(request.user.avatar, request.user.get_nickname(),
                                                '', request.user.username)
        content = {u'is_login': 1, u'user': {u'user_id': request.user.username, u'nickname': request.user.get_nickname(),
                    u'img_url': request.user.avatar, u'profile_url': u'', u'sign': sign_request(strToBeSigned.encode('utf-8'), SOCIALOAUTH_SITES[3][3]['client_secret'])}}
    else:
        content = {u'is_login': 0}
    return Response(content)

@api_view(['GET'])
@renderer_classes((JSONPRenderer,))
def sohucs_login(request):
    content = None
    try:
        userid = request.GET['user_id']
        if request.user.is_authenticated():
            if request.user.username != userid:
                #will logout changyan
                pass
        else:
            strToBeSigned = u'cy_user_id=%s&img_url=%s&nickname=%s&profile_url=%s&user_id=%s'\
                %(request.GET['cy_user_id'], request.GET['img_url'], request.GET['nickname'], request.GET['profile_url'], userid)
            if request.GET['sign'] == sign_request(strToBeSigned.encode('utf-8'),  SOCIALOAUTH_SITES[3][3]['client_secret']):
                # TODO user login
                content = {u'user_id': userid, 'reload_page': 1}
    except KeyError:
        pass
    if content is None:
        #logout changyan
        content = {u'user_id': '', 'reload_page': 1, 'js_src': [request.build_absolute_uri('%sjs/sohucs/logout.js' %(STATIC_URL))]}
    return Response(content)

def sohucs_waplogin(request):
    login_3rd_page(request)
        
@api_view(['GET'])
@renderer_classes((JSONPRenderer,))
def sohucs_logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    content = {u'code': 1, 'reload_page': 1}
    return Response(content)