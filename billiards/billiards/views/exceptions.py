# -*- coding: utf-8 -*-
# encoding: utf-8
from django.shortcuts import render_to_response
from billiards.settings import TEMPLATE_ROOT
from django.template.context import RequestContext

def handler404(request):
    return render_to_response(TEMPLATE_ROOT + '404.html', context_instance=RequestContext(request))

def handler500(request):
    return render_to_response(TEMPLATE_ROOT + '500.html', {'title': u'服务器休息一下', 'msg': u'一大波台球爱好者们正在访问此网站，服务器不堪重负，歇菜了，请稍候再访问'}, context_instance=RequestContext(request))

def handler403(request):
    return render_to_response(TEMPLATE_ROOT + '500.html', {'title': u'黑客来啦', 'msg': u'你没有访问该页面的权限'}, context_instance=RequestContext(request))
