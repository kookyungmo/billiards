from django.core.serializers.json import Serializer
from django.db.models.aggregates import Count
from django.http.response import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from billiards.commons import tojson2
from billiards.models import Assistant, AssistantOffer, assistantoffer_fields, Poolroom
from billiards.settings import TEMPLATE_ROOT


def assistant(request):
    return render_to_response(TEMPLATE_ROOT + 'escort/list.html', context_instance=RequestContext(request))


class AssistantOfferJSONSerializer(Serializer):
    def get_dump_object(self, obj):
        return self._current or {}
    
    def handle_field(self, obj, field):
        if field.name == 'poolroom':
            value = field._get_val_from_obj(obj)
            if value is not None:
                self._current[field.name] = Poolroom.objects.get(id=value).natural_key()
            else:
                self._current[field.name] = '{}';
        else:
            super(AssistantOfferJSONSerializer, self).handle_field(obj, field)

def assistant_list(request):
    assistantsOffers = AssistantOffer.objects.filter(status=1).filter(assistant__in=Assistant.objects.filter(state=1))\
        .annotate(dcount=Count('assistant'))
    jsonstr = tojson2(assistantsOffers, AssistantOfferJSONSerializer(), assistantoffer_fields)
    return HttpResponse(jsonstr)
