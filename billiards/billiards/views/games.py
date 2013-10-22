# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2013年10月22日

@author: kane
'''
from django.shortcuts import render_to_response
from billiards.models import Match
import datetime
from dateutil.relativedelta import relativedelta

template = 'foundation4/'
def index(request):
    date_after_week = datetime.datetime.today() + relativedelta(weeks=2)
    matches = Match.objects.filter(starttime__gte=datetime.datetime.now().strftime("%Y-%m-%d %H:%m")) \
        .exclude(starttime__gte=date_after_week.strftime("%Y-%m-%d %H:%m")).order_by('starttime')
    return render_to_response(template + 'games.html', {'matches': matches})