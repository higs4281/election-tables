import os, sys
import os, urllib, re
from collections import OrderedDict
import time, datetime
from datetime import timedelta
import json

import boto
from django.shortcuts import render_to_response, redirect, get_list_or_404, get_object_or_404
from django.core.mail import send_mail, mail_admins
from django.http import HttpResponse, HttpRequest
from django.template import loader, Context
from django.template.defaultfilters import slugify
from django.conf import settings

S3_KEY = os.getenv('S3_KEY')
S3_SECRET = os.getenv('S3_SECRET')

data_path = '/opt/django-projects/elections/data'
data_file = '%s/countydata.json' % data_path
county_file = '%s/voter_reg.json' % data_path
with open(county_file, 'r') as f:
    countydata = json.loads(f.read())
county_tuples = sorted([(countydata[fips]['name'], fips) for fips in countydata if fips != '12'])
tbcounties = ["Hernando", "Hillsborough", "Pasco", "Pinellas"]

def tables(request, prnt=False):
    rdate = datetime.datetime.now()
    YEAR = rdate.year
    with open(data_file, 'r') as f:
        data = json.loads(f.read())
    tstamp = data['tstamp']
    ordered = OrderedDict([(fips, data[fips]) for name, fips in county_tuples])
    cdict = {
        'ordered': ordered, 
        'counties': county_tuples, 
        'data': data, 
        'latest': tstamp,
        'tbcounties': tbcounties, 
        'fla': data['12']# '12' is fips code for florida
        }
    if prnt == False:
        return render_to_response('tables.html', cdict)
    else:
        response = HttpResponse(content_type='text/txt')
        response['Content-Disposition'] = 'attachment; filename=county%s-%s.txt' % (YEAR, slugify(tstamp))
        t = loader.get_template('print_tables.html')
        c = Context(cdict)
        response.write(t.render(c))
        return response
