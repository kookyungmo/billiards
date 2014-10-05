from django.shortcuts import render_to_response
from billiards.settings import TEMPLATE_ROOT
from django.template.context import RequestContext
from billiards.models import Assistant, assistant_fields, getThumbnailPath
from django.http.response import HttpResponse
from billiards.views.match import tojson
from django.utils import simplejson
from billiards import settings

def updateJsonStrWithCoverImage(assistantsJsonStr, assistants):        
    assistantObjs = simplejson.loads(assistantsJsonStr)
    for assistantObj in assistantObjs:
        for assistant in assistants:
            if str(assistant.uuid) == assistantObj['fields']['uuid']:
                assistantObj['fields']['coverimage'] = "%s%s" %(settings.MEDIA_URL[:-1], getThumbnailPath(assistant.coverimage, 300, 'h'))
                break
    return simplejson.dumps(assistantObjs)

def assistant(request):
    return render_to_response(TEMPLATE_ROOT + 'escort/list.html', context_instance=RequestContext(request))

def assistant_list(request):
    assistants = Assistant.objects.filter(state=1)
    jsonstr = tojson(assistants, assistant_fields)
    return HttpResponse(updateJsonStrWithCoverImage(jsonstr, assistants))
