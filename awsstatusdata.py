#!/bin/python

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
import logging
import sys
import pprint

logger = logging.getLogger('AWSStatusSkill')
logger.setLevel (logging.DEBUG)

AWS_DATA_URL = 'https://status.aws.amazon.com/data.json'

current_issues = []
archived_issues = []
service_map = {}
region_map = {}
archive_length = 0

service_code_pattern = re.compile ('([a-z0-9]+)-*([a-z0-9\-]*)')

def create_service_map ():
    resp = requests.get ('https://status.aws.amazon.com/')
    soup = BeautifulSoup (resp.text, 'html.parser')
    for table in soup.find_all ('table', class_ = 'fullWidth'):
        for tr in table.find_all ('tr'):
            td = tr.find ('td', class_ = 'bb top pad8')
            if td is not None:
                linktd = tr.find ('td', class_ = 'bb center top')
                if linktd is not None:
                    linka = linktd.find ('a')
                    service_name = td.text
                    names = service_name.split (' (')
                    service_name = str(names[0]).lower ()
                    if len(names) > 1:
                        region_name = str(names[1]).replace (')', '').lower ()
                    service_code = linka['href'].replace ('rss', '').replace ('/', '').replace ('.', '').lower ()
                    (service_code, region_code) = service_code_pattern.match (service_code).groups ()

                    service_map[service_name] = service_code.lower ()
                    if len(region_name) > 0:
                        region_map[region_name] = region_code.lower ()

def in_service_map (value):
    value = value.lower ()
    return value in service_map or value in service_map.values ()

def print_service_map ():
    print ("Showing {} known services:".format (len(service_map)))
    print ("\tShort Name                     Long Name")
    for k in service_map.keys ():
        print ("\t{} {}".format (service_map[k].ljust(30), k))

def get_service_code (value):
    value = str(value).lower ()
    if value in service_map:
        return service_map[value]
    if value in service_map.values ():
        return value 
    raise ValueError ('Specified value not foundin map')

def in_region_map (value):
    value = value.lower ()
    return value in region_map or value in region_map.values ()

def print_region_map ():
    print ("Showing {} known regions:".format (len(region_map)))
    print ("\tRegion Name          Region Code")
    for k in region_map.keys ():
        print ("\t{} {}".format (k.ljust(20), region_map[k]))

def get_region_code (value):
    value = str(value).lower ()
    if value in region_map:
        return region_map[value]
    if value in region_map.values ():
        return value
    raise ValueError ('Specified value not found in map')

def format_issue (issue):
    service_name = issue['service_name']
    region_name = ''
    try:
        names = issue['service_name'].split (" (")
        service_name = names[0]
        if len(names) > 1:
            region_name = names[1].replace (')', '')
    except:
        print ("Error pattern parsing {0}".format (issue['service_name']))

    (service_code, region_code) = service_code_pattern.match (issue['service']).groups ()
    summary = issue['summary']
    date = int(issue['date'])
    description = BeautifulSoup (issue['description'], 'html.parser').get_text ()

    return {'service_name': service_name, 
            'service_code': service_code,
            'region_name': region_name,
            'region_code': region_code,
            'summary': summary, 
            'date': date,
            'description': description}

def refresh_issues ():
    global archive_length

    resp = requests.get (AWS_DATA_URL)
    data = resp.json ()

    current = data['current']
    archive = data['archive']

    current_issues.clear ()
    for issue in current:
        current_issues.append (format_issue (issue))

    oldest_timestamp = int (time ())
    archived_issues.clear ()
    for issue in archive:
        if int (issue['date']) < oldest_timestamp:
            oldest_timestamp = int (issue['date'])
        archived_issues.append (format_issue (issue))

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

    current = [issue for issue in current_issues if issue_matches (issue)]
    current.sort (key = lambda x: x['date'], reverse = True)
    archive = [issue for issue in archived_issues if issue_matches (issue)]
    archive.sort (key = lambda x: x['date'], reverse = True)

    return {'current': current, 'archived': archive}

if __name__ == '__main__':
    create_service_map ()
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
            for issue in issues['current']:
                pprint.pprint (issue)
        if len(issues['archived']) > 0:
            print ("\nArchived Issues:")
            print ("----------------")
            for issue in issues['archived']:
                pprint.pprint (issue)
