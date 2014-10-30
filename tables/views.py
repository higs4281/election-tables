import os, sys
from django.shortcuts import render_to_response, redirect, get_list_or_404, get_object_or_404
from django.core.mail import send_mail, mail_admins
from django.http import HttpResponse, HttpRequest
from django.template import loader, Context
import os, urllib, re
from django.conf import settings
import time, datetime
from datetime import timedelta
import json
import boto

S3_KEY = os.getenv('S3_KEY')
S3_SECRET = os.getenv('S3_SECRET')

data_path = '/opt/django-projects/elections/data'
data_file = '%s/countydata.json' % data_path

def elex_tables(request, preview=False):
    """generates a styled print table of county results for a general election"""
    with open(data_file, 'r') as f:
        data = json.loads(f.read())
    tstamp = data['tstamp']
    startday = datetime.date.today()
    tbcounties = ["Hernando", "Hillsborough", "Pasco", "Pinellas"]
    results = []
    excluder = ['tstamp', 
                'prez_winner',
                'sen_winner',
                'prez_victory_votes',
                'prez_victory_comma',
                '12']
    for each in data.keys():
        if each not in excluder:
            results.append((data[each]['name'], 
                            {'obama': data[each]['obama'], 
                            'romney': data[each]['romney'], 
                            'nelson': data[each]['nelson'], 
                            'mack': data[each]['mack'], 
                            'leading_prez': data[each]['leading_prez'], 
                            'leading_sen': data[each]['leading_sen']}))
    results = sorted(results)
    florida = data['12']
    cdict = {
        'tstamp': tstamp,
        'precincts': data['12']['pcount'],
        'pre_pct': data['12']['ppct'],
        'results': results,
        'florida': florida,
        'tbcounties': tbcounties,
        }
    if preview == False:
        if senate == False:
            response = HttpResponse(mimetype='text/txt')
            response['Content-Disposition'] = 'attachment; filename=county2012%s.txt' % tstamp
            t = loader.get_template('elections/county.html')
            c = Context(cdict)
            response.write(t.render(c))
            return response
        else:
            response = HttpResponse(mimetype='text/txt')
            response['Content-Disposition'] = 'attachment; filename=county-sen2012%s.txt' % tstamp
            t = loader.get_template('elections/county-sen.html')
            c = Context(cdict)
            response.write(t.render(c))
            return response

    else:
        if senate == False:
            return render_to_response('elections/county-preview.html', cdict)
        else:
            return render_to_response('elections/county-sen-preview.html', cdict)



