from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import pandas as pd
import sheets
import time

SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]
ANALYTICS_ENDPOINT = "https://analyticsreporting.googleapis.com/v4/reports:batchGet"
KEY_FILE_LOCATION = "credentials.json"
VIEW_ID = "41509838"
START = datetime.datetime.toordinal(datetime.datetime(year=2021, month=1, day=1))
YESTERDAY = datetime.datetime.now().toordinal()
RANGE = YESTERDAY - START

# take notes and clean code


def initialize_analyticsreporting():
    # Initializes the API. Requires credentials and a service account within the GAnalytics account

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        KEY_FILE_LOCATION, SCOPES)

    # Build the service object.
    analytics = build('analyticsreporting', 'v4', credentials=credentials)

    return analytics


def get_report(analytics, segment, day):
    # This calls the API to generate a list of reports.
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
                                {'expression': 'ga:goalCompletionsAll', 'alias': 'Goals Completed'},
                                {'expression': 'ga:goalConversionRateAll', 'alias': 'Conversion %'},
                                {'expression': 'ga:goal7Completions', 'alias': 'VIP Submissions'},
                                {'expression': 'ga:goal18Completions', 'alias': 'Thank You Pages'},
                                {'expression': 'ga:goal2Completions', 'alias': 'Phone Calls'},
                                {'expression': 'ga:goal3Completions', 'alias': 'Home Tour Scheduled'},
                                {'expression': 'ga:goal5Completions', 'alias': 'Info Form Fills'},
                                {'expression': 'ga:goal1Completions', 'alias': 'Emails'}
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
                    'dimensions': [{'name': 'ga:segment'}, {'name': 'ga:channelGrouping'}],
                    # Granularity of data. If LARGE, very little sampling. SMALL, a lot of sampling
                    'samplingLevel': 'LARGE'
                }]
        }
    ).execute()


def get_my_numbers(response, day):
    # gets the reports
    to_df = []
    for report in response.get('reports', []):
        rows = report.get('data').get('rows')
        try:
            for row in rows:
                a_dictionary = {'Date': datetime.datetime.fromordinal(START + day).strftime('%Y-%m-%d'),
                                'Community': row.get('dimensions')[0],
                                'Channel': row.get('dimensions')[1],
                                'Web Traffic': row.get('metrics')[0].get('values')[0],
                                'Conversions': row.get('metrics')[0].get('values')[1],
                                'Conversion rate': f'{round(float(row.get("metrics")[0].get("values")[2]), 2)}%',
                                'Emails': row.get('metrics')[0].get('values')[8],
                                'Phone Calls': row.get('metrics')[0].get('values')[5],
                                'Home Tours Scheduled': row.get('metrics')[0].get('values')[6],
                                'Info Form Fills': row.get('metrics')[0].get('values')[7],
                                'VIP Submissions': row.get('metrics')[0].get('values')[3],
                                'Thank You Pages': row.get('metrics')[0].get('values')[4]
                                }
                to_df.append(a_dictionary)
            return to_df
        except TypeError:
            continue


def main(community, mode, header, day):
    # the main function which takes the segment 'community' and write and header modes. index is set to
    # false so i don't have to deal with random numbers in the first column
    # this calls the initialize function
    analytics = initialize_analyticsreporting()
    response = get_report(analytics, community, day)
    my_number = get_my_numbers(response, day)
    # print(my_number)
    df = pd.DataFrame(my_number)
    df.to_csv("analytics_test.csv", mode=mode, header=header, index=False)
    # TODO instead of df, can i just make a header row, then append a new line with the data?
    sheets.main()
    # sheets.append_the_sheet()
    time.sleep(.3)


if __name__ == '__main__':
    # this calls the main function
    # a list of the segments
    communities = ["wescott",
                   "maidstone-village",
                   "river-mill",
                   "central-crossing",
                   "rutland-grove",
                   "mosaic"]
    # loops through the list of segments
    for neighborhood in communities:
        # if it's the first item in the list, create the document and the headers. this will overwrite the
        # document if it already exists. this works because each community is sent to the DataFrame in batches
        # iterates through days as well, headers stop after day 1
        for day in range(0, RANGE):
            try:
                if neighborhood == communities[0] and day == 0:
                    main(neighborhood, "w", True, day)
                # if the item is not the first in the list, it appends to the existing document
                # under the current headers
                else:
                    main(neighborhood, "a", False, day)
            except IndexError:
                break
