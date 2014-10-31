import os, sys
import urllib, re
import time, datetime
from datetime import timedelta
import json

import boto

sys.path.append('/opt/django-projects/elections/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# from django.shortcuts import render_to_response, redirect, get_list_or_404, get_object_or_404
# from django.core.mail import send_mail, mail_admins
# from django.http import HttpResponse, HttpRequest
# from django.template import loader, Context
from django.utils.encoding import force_unicode

starter = datetime.datetime.now()
sname = os.path.basename(__file__).replace('.py', '')
starter = datetime.datetime.now()
YEAR = starter.year
print "%s is in the kitchen: %s" % (sname, starter.strftime('%c'))

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

def get_results():
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
    for each in gov.candidates:
        if each.party=='GOP':
            GOP = each
        if each.party=='Dem':
            DEM = each
        if each.party=='Lib':
            THIRD = each
    winner = None
    statewide = gov.get_reporting_unit('Florida1')
    gop_state_total, dem_state_total, third_state_total = 0, 0, 0
    for each in statewide.results:
        if each.candidate.is_winner:
            winner=each.candidate.name
        if each.candidate.party=="GOP":
            gop_state_total=each.vote_total
            gop_state_comma=intcomma(each.vote_total)
            gop_state_pct=roundone(each.vote_total_percent)
        if each.candidate.party=="Dem":
            dem_state_total=each.vote_total
            dem_state_comma=intcomma(each.vote_total)
            dem_state_pct=roundone(each.vote_total_percent)
        if each.candidate.party=="Lib":
            third_state_total=each.vote_total
            third_state_comma=intcomma(each.vote_total)
            third_state_pct=roundone(each.vote_total_percent)
    state_gov_leading = "no leader"
    state_gov_victory_votes, state_gov_victory_comma = None, None
    if gop_state_total > dem_state_total and gop_state_total > third_state_total:
        state_gov_leading = GOP.last_name
        state_gov_victory_votes = gop_state_total - dem_state_total
        state_gov_victory_comma = intcomma(state_gov_victory_votes)
    elif dem_state_total > gop_state_total and dem_state_total > third_state_total:
        state_gov_leading = DEM.last_name
        state_gov_victory_votes = dem_state_total - gov_state_total
        state_gov_victory_comma = intcomma(state_gov_victory_votes)
    elif third_state_total > gop_state_total and third_state_total > dem_state_total:
        state_gov_leading = THIRD.last_name
        state_gov_victory_votes = third_state_total - dem_state_total
        state_gov_victory_comma = intcomma(state_gov_victory_votes)
    timestamp = datetime.datetime.now()
#     dbstamp = Timestamp(stamp=timestamp, page="county results")
#     dbstamp.save()
#     tstamp_pk = dbstamp.pk
    tstamp = timestamp.strftime("%I:%M %p, %x")
    tstamp_slug = timestamp.strftime("%I%M%p")
    mapdict = {'winner': winner,
                'victory_votes': state_gov_victory_votes,
                'victory_comma': state_gov_victory_comma,
                'tstamp': tstamp, 
                '12': {
                    'name': "Florida",
                    'registered': statewide.num_reg_voters,
                    'stateVote': statewide.votes_cast, 
                    'ptotal': statewide.precincts_total, 
                    'pcount': statewide.precincts_reporting,
                    'ppct': roundone(statewide.precincts_reporting_percent), 
                    'leading_gov': state_gov_leading,
                    'dem': dem_state_total,
                    'dem_comma': dem_state_comma,
                    'dem_pct': dem_state_pct,
                    'gop': gop_state_total,
                    'gop_comma': gop_state_comma,
                    'gop_pct': gop_state_pct,
                    'third': third_state_total,
                    'third_comma': third_state_comma,
                    'third_pct': third_state_pct, 
                    }
                }
                
    for each in gov.counties:
        if each.fips=='12086':
            FIPS = '12025'
        else:
            FIPS = each.fips
        mapdict[FIPS]={'name': each.name, 
                            'pcount': each.precincts_reporting, 
                            'ptotal': each.precincts_total, 
                            'ppct': roundone(each.precincts_reporting_percent), 
                            'vcast': each.votes_cast,
                            'registered': each.num_reg_voters,
                            }
        for cand in each.results:
            if cand.candidate.party == 'GOP':
                mapdict[FIPS]['gop']=cand.vote_total
                mapdict[FIPS]['gop_comma']=intcomma(cand.vote_total)
                mapdict[FIPS]['gop_pct']=roundone(cand.vote_total_percent)
            elif cand.candidate.party == 'Dem':
                mapdict[FIPS]['dem']=cand.vote_total
                mapdict[FIPS]['dem_comma']=intcomma(cand.vote_total)
                mapdict[FIPS]['dem_pct']=roundone(cand.vote_total_percent)
            elif cand.candidate.party == 'Lib':
                mapdict[FIPS]['third']=cand.vote_total
                mapdict[FIPS]['third_comma']=intcomma(cand.vote_total)
                mapdict[FIPS]['third_pct']=roundone(cand.vote_total_percent)
        if mapdict[FIPS]['pcount']==0:
            mapdict[FIPS]['leading_gov']='no_results'
        elif mapdict[FIPS]['gop']>mapdict[FIPS]['dem']:
            mapdict[FIPS]['leading_gov']=GOP.last_name
            mapdict[FIPS]['victory_votes']=mapdict[FIPS]['gop']-mapdict[FIPS]['dem']
            mapdict[FIPS]['victory_votes_comma']=intcomma(mapdict[FIPS]['victory_votes'])
        elif mapdict[FIPS]['dem']>mapdict[FIPS]['gop']:
            mapdict[FIPS]['leading_gov']=DEM.last_name
            mapdict[FIPS]['victory_votes']=mapdict[FIPS]['dem']-mapdict[FIPS]['gop']
            mapdict[FIPS]['victory_votes_comma']=intcomma(mapdict[FIPS]['victory_votes'])
        else:
            mapdict[FIPS]['leading_gov']='tie'
    with open('/opt/django-projects/elections/data/voter_reg.json', 'r') as f:
        regd = json.loads(f.read())
        for key in regd:
            mapdict[key]['registered']=regd[key]['reg']

#     cdict = {
#         'timestamp': timestamp,
#         'tstamp': tstamp,
#         'precincts': precincts,
#         'pre_pct': pre_pct,
#         'results': mapdict,
#         'tbcounties': tbcounties,
#         }
#     slug=tstamp[:2]+tstamp[3:5]+tstamp[6:8]
#     response = HttpResponse(mimetype='text/txt')
#     response['Content-Disposition'] = 'attachment; filename=county2012-%s.txt' % slug
#     t = loader.get_template('elections/county.html')
#     c = Context(cdict)
#     response.write(t.render(c))
#     return response

    map_out="var R%s = %s;" % (YEAR, json.dumps(mapdict))
    data_out=json.dumps(mapdict)
    datafile = "/opt/django-projects/elections/data/countydata.json"
    with open(datafile, 'w') as f:
        f.write(data_out)
    datafile2 = "/opt/django-projects/elections/data/backups/countydata-%s.json" % tstamp_slug
    with open(datafile2, 'w') as f:
        f.write(data_out)
    rootkey="elections/%s/results/" % YEAR
    roots3="http://tbprojects.s3.amazonaws.com/%s" % rootkey
    jslug = "R%s.js" % YEAR

    # json bakery
    from boto.s3.key import Key
    s3=boto.connect_s3(os.getenv('S3_KEY'), os.getenv('S3_SECRET'))
    bucket = s3.create_bucket('tbprojects')
    k=Key(bucket)
    k.key="%sjs/R%s.js" % (rootkey, YEAR)
    k.content_type='application/javascript'
    k.set_contents_from_string(map_out)
    k.set_acl('public-read')
    URL1 = "%sjs/R%s.js" % (roots3, YEAR)
    print "baked R%s to:\n%s" % (YEAR, URL1)

    k.key="%sjs/backups/R%s_%s.js" % (rootkey, YEAR, tstamp_slug)
    k.content_type='application/javascript'
    k.set_contents_from_string(map_out)
    k.set_acl('public-read')
    print "baked R%s backup %s" % (YEAR, tstamp_slug)

    # print bakery
#     tablesuff = "tables/county%s.txt" % YEAR
#     from tables import views
#     x = HttpRequest()
#     k.key="%s%s" % (rootkey, tablesuff)
#     tmptxt = views.elex_tables(x)
#     k.content_type='application/octet-stream'
#     k.set_contents_from_string(tmptxt.content)
#     k.set_acl('public-read')
#     URL3 = "%s%s" % (roots3, tablesuff)
#     print "baked print table county%s to:\n%s" % (YEAR, URL3)


if __name__ == "__main__":
    get_results()

# winner code:        'is_winner': result.candidate.is_winner,    

########### MANUAL EXPORT 
# with open('/home/bhiggins/R2012.js', 'w') as f:
#     f.write("var R2012 = %s;" % json_out)

