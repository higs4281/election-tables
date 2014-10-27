import os, sys

from django.core.management import setup_environ
sys.path.append('/opt/django-projects/')
import represent.settings
setup_environ(represent.settings)
from represent.elections.models import Timestamp

from django.shortcuts import render_to_response, redirect, get_list_or_404, get_object_or_404
from django.core.mail import send_mail, mail_admins
from django.http import HttpResponse, HttpRequest
from django.template import loader, Context
import os, urllib, re
from django.contrib.gis.geos import Point
import time, datetime
from datetime import timedelta
import json
import boto
import re
from django.utils.encoding import force_unicode

starter = datetime.datetime.now()
sname = os.path.basename(__file__)
starter = datetime.datetime.now()
print "%s is in the kitchen: %s" % (sname, starter)

def roundit(flot):
    if flot > 0:
        pct = "%.2f" % round(flot, 2)
    else:
        pct = 0
    return pct

def roundone(flot):
    if flot > 0:
        pct = "%.1f" % round(flot, 1)
    else:
        pct = 0
    return pct

def intcomma(value):
    """
    Converts an integer to a string containing commas every three digits.
    For example, 3000 becomes '3,000' and 45000 becomes '45,000'.
    """
    orig = force_unicode(value)
    new = re.sub("^(-?\d+)(\d{3})", '\g<1>,\g<2>', orig)
    if orig == new:
        return new
    else:
        return intcomma(new)

def get_results(year):
    """posts these results files to s3: R[YEAR].js for maps and R[YEAR].txt for print"""
    from elections import AP
    startday = datetime.date.today()
    client = AP(os.getenv('AP_USER'), os.getenv('AP_PASS'))
    fla = client.get_state('FL')
#     prez = fla.filter_races(office_name='President')[0]
#     prez_winner = None
#     sen = fla.filter_races(office_name='U.S. Senate')[0]    
#     sen_winner = None
#     statewide = prez.get_reporting_unit('Florida1')
#     statewide_sen = sen.get_reporting_unit('Florida1')
#     obama_state_total, romney_state_total, nelson_state_total, mack_state_total = (0, 0, 0, 0)
    gov = fla.filter_races(office_name='Governor')[0]
    winner = None
    statewide = gov.get_reporting_unit('Florida1')
    gop_state_total, dem_state_total, 3rd_state_total = (0, 0, 0)
    #TK adjusting for gov race
    for each in statewide.results:
        if each.candidate.is_winner:
            winner=each.candidate.name
        if each.candidate.party=="Republican":
            obama_state_total=each.vote_total
            obama_state_comma=intcomma(each.vote_total)
            obama_state_pct=roundit(each.vote_total_percent)
        if each.candidate.last_name=="Romney":
            romney_state_total=each.vote_total
            romney_state_comma=intcomma(each.vote_total)
            romney_state_pct=roundit(each.vote_total_percent)
    for each in statewide_sen.results:
        if each.candidate.is_winner:
            sen_winner=each.candidate.name
        if each.candidate.last_name=="Nelson":
            nelson_state_total=each.vote_total
            nelson_state_comma=intcomma(each.vote_total)
            nelson_state_pct=roundit(each.vote_total_percent)
        if each.candidate.last_name=="Mack":
            mack_state_total=each.vote_total
            mack_state_comma=intcomma(each.vote_total)
            mack_state_pct=roundit(each.vote_total_percent)
    state_prez_leading, state_sen_leading = ("no leader", "no leader")
    if obama_state_total > romney_state_total:
        state_prez_leading = "obama"
        state_prez_victory_votes = obama_state_total - romney_state_total
        state_prez_victory_comma = intcomma(state_prez_victory_votes)
    if romney_state_total > obama_state_total:
        state_prez_leading = "romney"
        state_prez_victory_votes = romney_state_total - obama_state_total
        state_prez_victory_comma = intcomma(state_prez_victory_votes)
    if nelson_state_total > mack_state_total:
        state_sen_leading = "nelson"
    if mack_state_total > nelson_state_total:
        state_sen_leading = "mack"
    timestamp = datetime.datetime.now()
    dbstamp = Timestamp(stamp=timestamp, page="county results")
    dbstamp.save()
    tstamp_pk = dbstamp.pk
    tstamp = timestamp.strftime("%I:%M %p, %x")
    tstamp_slug = timestamp.strftime("%I%M%p")
    mapdict = {'prez_winner': prez_winner,
                'prez_victory_votes': state_prez_victory_votes,
                'prez_victory_comma': state_prez_victory_comma,
                'sen_winner': sen_winner,
                'tstamp': tstamp, 
                'tstamp_pk': tstamp_pk, 
                '12': {
                    'name': "Florida",
                    'registered': statewide.num_reg_voters,
                    'stateVote': statewide.votes_cast, 
                    'ptotal': statewide.precincts_total, 
                    'pcount': statewide.precincts_reporting,
                    'ppct': roundit(statewide.precincts_reporting_percent), 
                    'leading_sen': state_sen_leading,
                    'leading_prez': state_prez_leading,
                    'obama': obama_state_total,
                    'obama_comma': obama_state_comma,
                    'obama_pct': obama_state_pct,
                    'romney': romney_state_total,
                    'romney_comma': romney_state_comma,
                    'romney_pct': romney_state_pct,
                    'nelson': nelson_state_total,
                    'nelson_comma': nelson_state_comma,
                    'nelson_pct': nelson_state_pct, 
                    'mack': mack_state_total,
                    'mack_comma': mack_state_comma,
                    'mack_pct': mack_state_pct,
                    }
                }
    for each in prez.counties:
        if each.fips=='12086':
            FIPS = '12025'
        else:
            FIPS = each.fips
        mapdict[FIPS]={'name': each.name, 
                            'pcount': each.precincts_reporting, 
                            'ptotal': each.precincts_total, 
                            'ppct': roundit(each.precincts_reporting_percent), 
                            'vcast': each.votes_cast,
                            'registered': each.num_reg_voters,
                            }
        for cand in each.results:
            if "Obama" in cand.candidate.name:
                mapdict[FIPS]['obama']=cand.vote_total
                mapdict[FIPS]['obama_comma']=intcomma(cand.vote_total)
                mapdict[FIPS]['obama_pct']=roundit(cand.vote_total_percent)
            elif "Romney" in cand.candidate.name:
                mapdict[FIPS]['romney']=cand.vote_total
                mapdict[FIPS]['romney_comma']=intcomma(cand.vote_total)
                mapdict[FIPS]['romney_pct']=roundit(cand.vote_total_percent)
        if mapdict[FIPS]['pcount']==0:
            mapdict[FIPS]['leading_prez']='no_results'
        elif mapdict[FIPS]['obama']>mapdict[FIPS]['romney']:
            mapdict[FIPS]['leading_prez']='obama'
            mapdict[FIPS]['victory_votes']=mapdict[FIPS]['obama']-mapdict[FIPS]['romney']
            mapdict[FIPS]['victory_votes_comma']=intcomma(mapdict[FIPS]['victory_votes'])
        elif mapdict[FIPS]['romney']>mapdict[FIPS]['obama']:
            mapdict[FIPS]['leading_prez']='romney'
            mapdict[FIPS]['victory_votes']=mapdict[FIPS]['romney']-mapdict[FIPS]['obama']
            mapdict[FIPS]['victory_votes_comma']=intcomma(mapdict[FIPS]['victory_votes'])
        else:
            mapdict[FIPS]['leading_prez']='tie'

    for each in sen.counties:
        if each.fips=='12086':
            FIPS = '12025'
        else:
            FIPS = each.fips
        for cand in each.results:
            if "Nelson" in cand.candidate.name:
                mapdict[FIPS]['nelson']=cand.vote_total
                mapdict[FIPS]['nelson_comma']=intcomma(cand.vote_total)
                mapdict[FIPS]['nelson_pct']=roundit(cand.vote_total_percent)
            elif "Mack" in cand.candidate.name:
                mapdict[FIPS]['mack']=cand.vote_total
                mapdict[FIPS]['mack_comma']=intcomma(cand.vote_total)
                mapdict[FIPS]['mack_pct']=roundit(cand.vote_total_percent)
        if mapdict[FIPS]['pcount']==0:
            mapdict[FIPS]['leading_sen']='no_results'
        elif mapdict[FIPS]['nelson']>mapdict[FIPS]['mack']:
            mapdict[FIPS]['leading_sen']='nelson'
        elif mapdict[FIPS]['mack']>mapdict[FIPS]['nelson']:
            mapdict[FIPS]['leading_sen']='mack'
        else:
            mapdict[FIPS]['leading_sen']='tie'
    map_out="var R2012 = %s;" % json.dumps(mapdict)
    data_out=json.dumps(mapdict)
    datafile = "/opt/django-projects/represent/data/countydata.json"
    with open(datafile, 'w') as f:
        f.write(data_out)
    datafile2 = "/opt/django-projects/represent/data/backups/countydata-%s.json" % tstamp_slug
    with open(datafile2, 'w') as f:
        f.write(data_out)
    rootkey="elections/2012/results/"
    roots3="http://tbprojects.s3.amazonaws.com/%s" % rootkey
    jslug = "R2012.js"

    # json bakery
    from boto.s3.key import Key
    s3=boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    bucket = s3.create_bucket('tbprojects')
    k=Key(bucket)
    k.key="%sjs/R2012.js" % rootkey
    k.content_type='application/javascript'
    k.set_contents_from_string(map_out)
    k.set_acl('public-read')
    URL1 = "%sjs/R2012.js" % roots3
    print "baked R2012 to:\n%s" % URL1

    k.key="%sjs/backups/R2012_%s.js" % (rootkey, tstamp_slug)
    k.content_type='application/javascript'
    k.set_contents_from_string(map_out)
    k.set_acl('public-read')
    print "baked R2012 backup %s" % tstamp_slug

    # print bakery
    tablesuff = "tables/county2012.txt"
    from represent.elections import views
    x = HttpRequest()
    k.key="%s%s" % (rootkey, tablesuff)
    tmptxt = views.elex2012(x)
    k.content_type='application/octet-stream'
    k.set_contents_from_string(tmptxt.content)
    k.set_acl('public-read')
    URL3 = "%s%s" % (roots3, tablesuff)
    print "baked print table county2012 to:\n%s" % URL3

    tablesuff2 = "tables/county-sen2012.txt"
    x = HttpRequest()
    k.key="%s%s" % (rootkey, tablesuff2)
    tmptxt = views.elex2012(x, senate=True)
    k.content_type='application/octet-stream'
    k.set_contents_from_string(tmptxt.content)
    k.set_acl('public-read')
    URL4 = "%s%s" % (roots3, tablesuff2)
    print "baked print table county-sen2012 to:\n%s" % URL4


if __name__ == "__main__":
    get_2012_results()

# winner code:        'is_winner': result.candidate.is_winner,    

########### MANUAL EXPORT 
# with open('/home/bhiggins/R2012.js', 'w') as f:
#     f.write("var R2012 = %s;" % json_out)

