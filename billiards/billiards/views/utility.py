# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2014年1月5日

@author: kane
'''
from django.shortcuts import render_to_response
from billiards.settings import TEMPLATE_ROOT
from django.template.context import RequestContext
'''
Base on a responsive web page template that works well on IE7 and IE8.
It won't work on IE6, but it also gives very simple text for information.
http://www.prowebdesign.ro/simple-responsive-template-free/
'''
def unsupportedbrowser(request):
    return render_to_response(TEMPLATE_ROOT + 'unsupportedbrowser.html',
                              {},
                              context_instance=RequestContext(request))