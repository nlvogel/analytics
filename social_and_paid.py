from apiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import pandas as pd
import sheets
import time
from communities import communities, START, neighborhood_check
import csv
from floor_plans import now

SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]
ANALYTICS_ENDPOINT = "https://analyticsreporting.googleapis.com/v4/reports:batchGet"
KEY_FILE_LOCATION = "credentials.json"
VIEW_ID = "41509838"
# START = datetime.datetime.toordinal(datetime.datetime(year=2021, month=10, day=27))
# END = datetime.datetime.toordinal(datetime.datetime(year=2022, month=1, day=1))
YESTERDAY = datetime.datetime.now().toordinal()
RANGE = YESTERDAY - START
# RANGE = END - START
SHEET = '1CbepUNJarwt_VelDKZHv-DfdLHONXjwicn0eUL0fefA'

# take notes and clean code


def initialize_analyticsreporting():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        KEY_FILE_LOCATION, SCOPES)
    analytics = build('analyticsreporting', 'v4', credentials=credentials)
    return analytics


def get_report(analytics, segment, day):
    return analytics.reports().batchGet(
        body={
            'reportRequests': [
                {
                    # The GAnalytics view ID given within the console
                    'viewId': VIEW_ID,
                    # Can have two date ranges, the second will be a comparison.
                    # YYYY-MM-DD format as provided by strftime
                    'dateRanges': [{'startDate': datetime.datetime.fromordinal(START + day).strftime('%Y-%m-%d'),
                                    'endDate': datetime.datetime.fromordinal(START + day).strftime('%Y-%m-%d')}],
                    # The numbers you're searching for. As far as I could tell, there's no limit
                    'metrics': [{'expression': 'ga:sessions', 'alias': 'Web Traffic'},
                                {'expression': 'ga:goalCompletionsAll', 'alias': 'Goals Completed'}
                                ],
                    # A dynamic segment. dimensionFilter is where the magic happens
                    'segments': [
                        {
                            "dynamicSegment":
                                {
                                    # names the segment after the expression. Title cases and strips hyphens
                                    "name": segment.title().replace("-", " "),
                                    "sessionSegment":
                                        {
                                            "segmentFilters": [
                                                {
                                                    "simpleSegment":
                                                        {
                                                            "orFiltersForSegment": [
                                                                {
                                                                    "segmentFilterClauses": [
                                                                        {
                                                                            "dimensionFilter":
                                                                                {
                                                                                    # what you want to segment
                                                                                    # how you want to search for the
                                                                                    # segment
                                                                                    # what you're segmenting
                                                                                    # PARTIAL, EXACT, REGEXP are
                                                                                    # common uses
                                                                                    "dimensionName": "ga:pagePath",
                                                                                    "operator": "REGEXP",
                                                                                    "expressions": [segment]
                                                                                }
                                                                        }

                                                                    ]
                                                                }
                                                            ]
                                                        }}
                                            ]
                                        }}}],
                    # Must contain at least the segment dimension if a segment is included
                    'dimensions': [{'name': 'ga:segment'},
                                   {'name': 'ga:medium'},
                                   {'name': 'ga:channelGrouping'},],
                    'dimensionFilterClauses': [
                        {
                            'operator': 'OR',
                            'filters': [
                                {
                                    'dimensionName': 'ga:sourceMedium',
                                    'operator': 'EXACT',
                                    'expressions': "google / cpc"
                                },
                                {
                                    'dimensionName': 'ga:medium',
                                    'operator': 'EXACT',
                                    'expressions': 'social'
                                },
                                # { not using this filter?
                                #     'dimensionName': 'ga:pagePath',
                                #     'operator': 'REGEXP',
                                #     'expressions': 'floorplan|floor-plan'
                                # }
                            ]
                        }
                    ],
                    # Granularity of data. If LARGE, very little sampling. SMALL, a lot of sampling
                    'samplingLevel': 'LARGE'
                }]
        }
    ).execute()


def get_my_numbers(response, day, region):
    for report in response.get('reports', []):
        rows = report.get('data').get('rows')
        try:
            for row in rows:
                data_list = [
                    datetime.datetime.fromordinal(START + day).strftime('%Y-%m-%d'),
                    region,
                    row.get('dimensions')[0],
                    row.get('dimensions')[1],
                    row.get('metrics')[0].get('values')[0],
                    row.get('metrics')[0].get('values')[1]
                ]
                if data_list[2] == '/Wescott/':
                    data_list[2] = 'Wescott TH'
                elif data_list[2] == 'Governors Retreat':
                    data_list[2] = 'Governor\'s Retreat'
                elif data_list[2] == 'Fox Creek Homestead':
                    data_list[2] = 'Wynwood SF'
                elif data_list[2] == 'Fox Creek Cottages':
                    data_list[2] = 'Wynwood Cottages'
                elif data_list[2] == '/Giles/':
                    data_list[2] = 'Giles Farm'
                elif data_list[2] == 'Giles Townhomes' or data_list[2] == 'The Townes At Giles':
                    data_list[2] = 'Giles Farm TH'
                elif data_list[2] == '/Magnolia Green/':
                    data_list[2] = 'Glen Abbey at Magnolia Green'
                elif data_list[2] == 'Magnolia Green Townhomes':
                    data_list[2] = 'Palisades Cove Magnolia Green'
                elif data_list[2] == 'Quarterpath At Williamsburg Condos':
                    data_list[2] = 'Quarter Path Condos'
                elif data_list[2] == 'Enclave At Leesville' or data_list[2] == 'Enclaveatleesville':
                    data_list[2] = 'Enclave'
                elif data_list[2] == 'The Reserve At Wackena':
                    data_list[2] = 'Wackena'
                elif data_list[2] == 'Taylor Farm':
                    data_list[2] = 'Taylor Farm SF'
                elif data_list[2] == 'Mosaic':
                    data_list[2] = 'Mosaic at West Creek TH'
                elif data_list[2] == '/River Mill/':
                    data_list[2] = 'River Mill SF'
                if row.get('dimensions')[2] == 'Paid Search' and data_list[3] == 'cpc':
                    data_list[3] = 'Paid Search Ads'
                elif row.get('dimensions')[2] == 'Display' and data_list[3] == 'cpc':
                    data_list[3] = 'Paid Display Ads'
                elif data_list[3] == 'social':
                    data_list[3] = 'Organic Social Media'
                # sheets.append_sheet([data_list], SHEET, 'Social and Paid Sources!A2')
                with open(f'{now}-social_and_paid.csv', mode='a') as f:
                    writer = csv.writer(f)
                    writer.writerow(data_list)
                # time.sleep(.5)
        except TypeError:
            continue


def main(community, day, region):
    # sheets.sheets_auth()
    analytics = initialize_analyticsreporting()
    response = get_report(analytics, community, day)
    get_my_numbers(response, day, region)


if __name__ == '__main__':
    # communities = ["wescott"]
    # time.sleep(60)
    for day in range(0, RANGE):
        # time.sleep(1)
        for neighborhood in communities:
            try:
                region = neighborhood_check(neighborhood)
                main(neighborhood, day, region)
                # time.sleep(1)
            except HttpError as err:
                print(err)
                continue
            except IndexError:
                break
    import os
    os.system('afplay /System/Library/Sounds/Sosumi.aiff')