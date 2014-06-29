from django.shortcuts import render_to_response
from billiards.settings import TEMPLATE_ROOT
from django.template.context import RequestContext

def game_2048(request):
    return render_to_response(TEMPLATE_ROOT + 'event/redbull_2048.html', context_instance=RequestContext(request))
