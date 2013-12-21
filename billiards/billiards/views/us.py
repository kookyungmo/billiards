from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from billiards.settings import TEMPLATE_ROOT
from django.template.context import RequestContext

def aboutus(request):
    return render_to_response(TEMPLATE_ROOT + 'aboutus.html', context_instance=RequestContext(request))

def joinus(request):
    return render_to_response(TEMPLATE_ROOT + 'joinus.html', context_instance=RequestContext(request))

def contactus(request):
    return render_to_response(TEMPLATE_ROOT + 'contactus.html', context_instance=RequestContext(request))

def cooperation(request):
    return render_to_response(TEMPLATE_ROOT + 'cooperation.html', context_instance=RequestContext(request))
