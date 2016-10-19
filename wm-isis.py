#!/usr/bin/python

#Author Maikel de Boer - maikel.deboer@hibernianetworks.com

import re, sys
from jnpr.junos import Device

configdir = '/var/www/weathermap/'
configfile = 'weathermap.conf'
routerusername = 'username'
routerpassword = 'password'
router = 'hostname'

def get_juniper_isis_database():
    #Get isis database from a Juniper and clean it a bit
    #Tested on Juniper MX 480 runnnig 14.2R5.8
    isis_database = []
    try :
        dev = Device(host=router, user=routerusername, passwd=routerpassword)
        dev.open()
        isisdb = dev.cli("show isis database detail")
        dev.close()
    except:
    print 'Unable to connect to %s' % router
    sys.exit(2)

    for line in isisdb.splitlines():
        if re.match('.*Sequence.*', line):
        a_router = re.search('.*\.', line)
        a_router = a_router.group()[:-1]
        a_router = a_router.replace('-re0', '')
        a_router = a_router.replace('-re1', '')
    if re.match('.*IS neighbor:.*', line):
        b_router = re.search('(.*IS neighbor: )(.*)(\.0.*Metric:)(.*\d)'\
                , line)
            metric = b_router.group(4).strip()
        b_router = b_router.group(2)
            b_router = b_router.replace('-re0', '')
            b_router = b_router.replace('-re1', '')

        isis_database.append((a_router, b_router, metric))
    return isis_database

def generate_wm(database):
    config = ''
    #Generate new weathermap with isis metrics on it
    handle = open(configdir + configfile, 'r')
    for line in handle.readlines():
    if not re.match('.*INCOMMENT.*', line) and not re.match('.*OUTCOMMENT.*', line):
             config += line
        if re.match('LINK .*-.*', line) :
        #print line
        search = re.search('(LINK )(.*)(-)(.*)', line)
        router_a = search.group(2)
        router_b = search.group(4)

        metric_a = metric_lookup(database, router_a, router_b)
        metric_b = metric_lookup(database, router_b, router_a)
        #print metric_a
        #print metric_b

        config += '\tOUTCOMMENT \t %s\n' % metric_a
        config += '\tINCOMMENT \t %s\n' % metric_b

    handle = open(configdir + configfile, 'w')
    handle.write(config)
    handle.close()

def metric_lookup(database, router_a, router_b):
    returndata = ''
    for line in database:
    if line[0] == router_a and line[1] == router_b:
        returndata = line[2]
    return returndata

def main():
    database = get_juniper_isis_database()
    generate_wm(database)

main()
