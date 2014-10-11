from django.db.models.aggregates import Count
from django.http.response import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from billiards.commons import tojson2, NoObjectJSONSerializer
from billiards.models import Assistant, AssistantOffer, assistantoffer_fields, Poolroom,\
    assistant_fields, AssistantImage,\
    assistantimage_fields
from billiards.settings import TEMPLATE_ROOT
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson


def assistant(request):
    return render_to_response(TEMPLATE_ROOT + 'escort/list.html', context_instance=RequestContext(request))
    
class AssistantJSONSerializer(NoObjectJSONSerializer):
    def handle_field(self, obj, field):
        if field.name == 'poolroom':
            value = field._get_val_from_obj(obj)
            if value is not None:
                self._current[field.name] = Poolroom.objects.get(id=value).natural_key()
            else:
                self._current[field.name] = '{}';
        else:
            super(AssistantJSONSerializer, self).handle_field(obj, field)

def assistant_list(request):
    assistantsOffers = AssistantOffer.objects.filter(status=1).filter(assistant__in=Assistant.objects.filter(state=1))\
        .annotate(dcount=Count('assistant'))
    jsonstr = tojson2(assistantsOffers, AssistantJSONSerializer(), assistantoffer_fields)
    return HttpResponse(jsonstr)

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
            assistantobj[0]['images'] = simplejson.loads(tojson2(AssistantImage.objects.filter(assistant=assistant).filter(status=1), 
                                                                 AssistantJSONSerializer(), assistantimage_fields))
            return HttpResponse(simplejson.dumps(assistantobj))
        except Assistant.DoesNotExist:
            return HttpResponse({'error': 'not found', 'code': 0})