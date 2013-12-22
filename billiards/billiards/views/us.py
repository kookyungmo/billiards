from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from billiards.settings import TEMPLATE_ROOT
from django.template.context import RequestContext

def about(request):
    return render_to_response(TEMPLATE_ROOT + 'about.html', context_instance=RequestContext(request))

def join(request):
    return render_to_response(TEMPLATE_ROOT + 'join.html', context_instance=RequestContext(request))

def contact(request):
    return render_to_response(TEMPLATE_ROOT + 'contact.html', context_instance=RequestContext(request))

def partner(request):
    return render_to_response(TEMPLATE_ROOT + 'partner.html', context_instance=RequestContext(request))
