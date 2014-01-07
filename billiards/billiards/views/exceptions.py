from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from billiards.settings import TEMPLATE_ROOT
from django.template.context import RequestContext

def handler404(request):
    return render_to_response(TEMPLATE_ROOT + '404.html', context_instance=RequestContext(request))

def handler500(request):
    return render_to_response(TEMPLATE_ROOT + '404.html', context_instance=RequestContext(request))
