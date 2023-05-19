#!/usr/bin/env python3

"""
Retrieve the latest service health data from https://status.aws.amazon.com/data.json and
process it to build a database of service outtages.

https://status.aws.amazon.com/ contains a list of services and their regions in unfriendly
Javascript and HTML.
"""
import requests
import re
from bs4 import BeautifulSoup
from time import time
from datetime import datetime
import logging
import sys
import pprint
import json
from dateutil.parser import parse as dateutil_parse
from dateutil import tz as dateutil_tz
# dateutil needs to be configured to recognize PST / PDT as West Coast time zones
PACIFIC = dateutil_tz.gettz("America/Los_Angeles")
timezone_info = {"PST": PACIFIC, "PDT": PACIFIC}

logger = logging.getLogger('AWSStatusSkill')
logger.setLevel (logging.DEBUG)

AWS_DATA_URL = 'https://history-events-eu-west-1-prod.s3.amazonaws.com/historyevents.json'
AWS_SERVICE_URL = 'https://d3s31nlw3sm5l8.cloudfront.net/services.json'

current_issues = []
archived_issues = []
service_map = {}
region_map = {}
archive_length = 0

service_code_pattern = re.compile ('([a-z0-9]+)-*([a-z0-9\-]*)')

def create_region_service_map ():
    resp = requests.get (AWS_SERVICE_URL)
    svc_data = resp.json ()

    region_map['Global'] = ''

    for svc_detail in svc_data:
        service_name = svc_detail['service_name']
        service_code = svc_detail['service']

        region_code = svc_detail['region_id'] if 'region_id' in svc_detail else None
        region_name = svc_detail['region_name'] if 'region_name' in svc_detail else None

        if region_code is not None and len (region_code) > 0:
            service_code = service_code.replace(f'-{region_code}', '')

        service_map[service_name] = service_code
        if region_name is not None and len(region_name) > 0:
            region_map[region_name] = region_code


def in_service_map (value):
    value = value.lower ()
    return value in service_map or value in service_map.values ()

def print_service_map ():
    print ("Showing {} known services:".format (len(service_map)))
    print ("\tShort Name                     Long Name")
    for k in sorted(service_map):
        print ("\t{} {}".format (service_map[k].ljust(30), k))

def get_service_name (value):
    if value is None:
        raise ValueError ('Specified value is empty')
    keys = [k for k, v in service_map.items() if v == value]
    return keys[0]

def get_service_code (value):
    value = str(value).lower ()
    if value in service_map:
        return service_map[value]
    if value in service_map.values ():
        return value 
    raise ValueError ('Specified value not found in map')

def in_region_map (value):
    return value in region_map or value in region_map.values ()

def print_region_map ():
    print ("Showing {} known regions:".format (len(region_map)))
    print ("\tRegion Name          Region Code")
    for k in sorted(region_map):
        print ("\t{} {}".format (k.ljust(20), region_map[k]))

def get_region_name (value):
    if value is None:
        raise ValueError ('Specified value is empty')
    keys = [k for k, v in region_map.items() if v == value]
    return keys[0]

def get_region_code (value):
    if value in region_map:
        return region_map[value]
    if value in region_map.values ():
        return value
    raise ValueError ('Specified value not found in map')

def format_issue (issue):
    service_code = issue['service_code']
    region_code = issue['region_code']

    # (service_code, region_code) = service_code_pattern.match (issue['service']).groups ()
    event_log = issue['event_log']
    summary = event_log[0]['summary']
    unixdate = int(issue['date'])
    utcdate = datetime.utcfromtimestamp(unixdate).strftime('%Y-%m-%d %H:%M:%S')
    timeline = []
    mintimestamp = None
    maxtimestamp = None
    for event in event_log:
        event_timestamp = event['timestamp']
        dtstamp = datetime.utcfromtimestamp(event_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        timeline.append ((dtstamp, event['message']))
        if mintimestamp is None or event_timestamp < mintimestamp:
            mintimestamp = event_timestamp
        if maxtimestamp is None or event_timestamp > maxtimestamp:
            maxtimestamp = event_timestamp

    duration = int(maxtimestamp - mintimestamp)/60

    service_name = get_service_name (service_code)
    region_name = get_region_name (region_code)
    return {'service_name': service_name,
            'service_code': service_code,
            'region_name': region_name,
            'region_code': region_code,
            'summary': summary,
            'timestamp': unixdate,
            'date': utcdate,
            'description': 'DEPRECATED',
            'timeline': timeline,
            'duration_mins': duration}

def refresh_issues ():
    global archive_length

    resp = requests.get (AWS_DATA_URL)
    data = resp.json ()

    current_issues.clear ()
    archived_issues.clear ()
    oldest_timestamp = int (time ())
    for service_code in service_map.values():
        for region_code in region_map.values ():
            service_region_code = service_code
            if len(region_code) > 0:
                service_region_code = f'{service_code}-{region_code}'


            if service_region_code in data:
                for event in data[service_region_code]:
                    event['service_code'] = service_code
                    event['region_code'] = region_code

                    event_resolved = False
                    for entry in event['event_log']:
                        if entry['status'] == "0":
                            event_resolved = True

                    if event_resolved:
                        if int (event['date']) < oldest_timestamp:
                            oldest_timestamp = int (event['date'])
                        archived_issues.append (format_issue (event))
                    else:
                        current_issues.append (format_issue (event))

    archive_length = int ((time () - oldest_timestamp) / (24 * 60 * 60))
    logger.info ("Retrieved issues spanning {} days".format (archive_length))

def get_service_issues (service = None, region = None):
    """
    Return a dict containing a sorted list named 'current' of issue objects along
    with a sorted list named 'achived' of issue objects.
    """
    def issue_matches (issue):
        if service is None and region is None:
            return True

        if service is not None:
            if issue['service_name'].lower () == service or issue['service_code'].lower () == service:
                if region is None:
                    return True
                else:
                    return issue['region_name'].lower () == region or issue['region_code'].lower () == region
        elif region is not None:
            return issue['region_name'].lower () == region or issue['region_code'].lower () == region
        
        return False

    print("getting issues for {} in {}".format (service, region))

    current = [issue for issue in current_issues if issue_matches (issue)]
    current.sort (key = lambda x: x['date'], reverse = True)
    archive = [issue for issue in archived_issues if issue_matches (issue)]
    archive.sort (key = lambda x: x['date'], reverse = True)

    return {'current': current, 'archived': archive}

if __name__ == '__main__':
    create_region_service_map ()
    refresh_issues ()
    print ("{0} known services and {1} regions".format (len(service_map), len(region_map)))
    print ("{} current issues, {} archived issues for {} days".format (len(current_issues), len(archived_issues), archive_length))

    if len(sys.argv) <= 1:
        print ("For more specific detail please specify a service name, region name, or both.")
        print ("For a list of services specify 'services', for a list of regions specify 'regions'.")
        print ("Example Usage:")
        print ("\t$> {} services".format (sys.argv[0]))
        print ("\t$> {} lambda eu-west-1".format (sys.argv[0]))

    if len(sys.argv) > 1:
        service = None
        region = None

        if sys.argv[1] == 'regions':
            print_region_map ()
            sys.exit (0)

        if sys.argv[1] == 'services':
            print_service_map ()
            sys.exit (0)

        if in_service_map (sys.argv[1]):
            service = sys.argv[1]
        if in_region_map (sys.argv[1]):
            region = sys.argv[1]

        if len(sys.argv) > 2:
            if in_service_map (sys.argv[2]):
                service = sys.argv[2]
            if in_region_map (sys.argv[2]):
                region = sys.argv[2]

        issues = get_service_issues (service = service, region = region)

        region_label = 'all regions'
        if region is not None:
            region_label = get_region_code (region)

        service_label = 'all services'
        if service is not None:
            service_label = get_service_code (service)

        print ("{} current issues, {} archived issues for {} in {}".format (len (issues['current']), len(issues['archived']), service_label, region_label))
        if len(issues['current']) > 0:
            print ("\nCurrent Issues:")
            print ("---------------")
            print (json.dumps(issues['current'], sort_keys = True, indent = 4))
        if len(issues['archived']) > 0:
            print ("\nArchived Issues:")
            print ("----------------")
            print (json.dumps(issues['archived'], sort_keys = True, indent = 4))
