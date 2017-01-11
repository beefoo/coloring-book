# -*- coding: utf-8 -*-

import argparse
import csv
from datetime import datetime
import os
import sys
import urllib2

# input
parser = argparse.ArgumentParser()
parser.add_argument('-url', dest="URL", default="https://tidesandcurrents.noaa.gov/inundation/Analysis?datum=MHHW&userReferrence=&beginDate=%s&endDate=%s&submit=+Submit++", help="URL pattern")
parser.add_argument('-stations', dest="STATIONS", default="8534720,8575512,8658120,8665530", help="List of stations")
parser.add_argument('-y0', dest="START_YEAR", type=int, default=1951, help="Start year")
parser.add_argument('-y1', dest="END_YEAR", type=int, default=2015, help="End year")
parser.add_argument('-yi', dest="YEAR_INCR", type=int, default=5, help="Years to increment by")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/%s_InundationAnalysis.csv", help="Output file pattern")

# init input
args = parser.parse_args()
URL = args.URL
STATIONS = args.STATIONS.split(",")
START_YEAR = args.START_YEAR
END_YEAR = args.END_YEAR
YEAR_INCR = args.YEAR_INCR
OUTPUT_FILE = args.OUTPUT_FILE

HEADERS = ["Period Start", "Period End", "Time of High Tide", "Elevation (Meters) Above Datum", "Tide Type", "Duration (Hours)"]

def readCSV(filename):
    data = []
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            reader = csv.DictReader(f)
            data = list(reader)
    return data

for station in STATIONS:
    year = START_YEAR
    filename = OUTPUT_FILE % station
    stationData = []
    while year < END_YEAR:
        beginDate = "%s0101" % year
        endDate =  "%s1231" % (year + YEAR_INCR - 1)
        print URL % (beginDate, endDate)
        # getUrl = URL % (station, beginDate, endDate)
        # # Download HTML if it doesn't exist
        # htmlFilename = "html/%s_%s_%s.html" % (station, beginDate, endDate)
        # if not os.path.isfile(htmlFilename):
        #     with open(htmlFilename, 'wb') as f:
        #         print "Downloading: %s" % getUrl
        #         f.write(urllib2.urlopen(getUrl).read())
        #         f.close()
        #         print "Downloaded: %s" % htmlFilename
        year += YEAR_INCR
    break
