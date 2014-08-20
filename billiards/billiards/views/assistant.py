from django.shortcuts import render_to_response
from billiards.settings import TEMPLATE_ROOT
from django.template.context import RequestContext

def assistant(request):
    return render_to_response(TEMPLATE_ROOT + 'assistant.html', context_instance=RequestContext(request))

def assistant1(request):
    return render_to_response(TEMPLATE_ROOT + 'assistant-1.html', context_instance=RequestContext(request))

def xiaohui(request):
    return render_to_response(TEMPLATE_ROOT + 'xiaohui.html', context_instance=RequestContext(request))

def ruoyu(request):
    return render_to_response(TEMPLATE_ROOT + 'ruoyu.html', context_instance=RequestContext(request))

def meixi(request):
    return render_to_response(TEMPLATE_ROOT + 'meixi.html', context_instance=RequestContext(request))

def yangyang(request):
    return render_to_response(TEMPLATE_ROOT + 'yangyang.html', context_instance=RequestContext(request))

def xiaoxu(request):
    return render_to_response(TEMPLATE_ROOT + 'xiaoxu.html', context_instance=RequestContext(request))

def shanshan(request):
    return render_to_response(TEMPLATE_ROOT + 'shanshan.html', context_instance=RequestContext(request))

def wawa(request):
    return render_to_response(TEMPLATE_ROOT + 'wawa.html', context_instance=RequestContext(request))
