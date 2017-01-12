# -*- coding: utf-8 -*-

import argparse
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import os
from pprint import pprint
import re
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-dir', dest="HTML_DIR", default="html", help="URL pattern")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/%s_InundationAnalysis.csv", help="Output file pattern")

# init input
args = parser.parse_args()
HTML_DIR = args.HTML_DIR
OUTPUT_FILE = args.OUTPUT_FILE

# config
HEADER = ["Station", "Period Start", "Period End", "Time of High Tide", "Elevation (Meters) Above Datum", "Tide Type", "Duration (Hours)"]

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def readCSV(filename):
    data = []
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            reader = csv.reader(f)
            next(reader, None) # skip header
            data = list(reader)
    return data

def saveCSV(filename, data):
    with open(filename, 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        for row in data:
            writer.writerow(row)
        print "Wrote %s rows to file: %s" % (len(data), filename)

# Go through each html file
for fname in os.listdir(HTML_DIR):
    if not fname.endswith('.html'):
        continue

    # Retrieve station data if it exists
    station = fname[:7]
    stationFilename = OUTPUT_FILE % station
    stationData = readCSV(stationFilename)

    with open(HTML_DIR + "/" + fname,'rb') as f:
        contents = BeautifulSoup(f, 'html.parser')
        rows = contents.findAll(True, {'class':['tableRowEven', 'tableRowOdd']})
        for i, row in enumerate(rows):
            cols = row.findAll('td')
            if (len(cols)+1) != len(HEADER):
                print "Warning: %s row %s does not match header cols" % (station, i+1)
                continue
            thisRow = [station]
            for j, col in enumerate(cols):
                thisCol = col.get_text()
                thisCol = re.sub(r'&[a-z]+;', '', thisCol)
                thisCol = thisCol.strip()
                thisRow.append(thisCol)
            # Check if row already exists
            exists = [d for d in stationData if d[0]==thisRow[0] and d[1]==thisRow[1] and d[2]==thisRow[2]]
            if not len(exists):
                stationData.append(thisRow)

    # Sort station data
    stationData = sorted(stationData, key=lambda k: k[1]) # Sort by date
    stationData = sorted(stationData, key=lambda k: k[0]) # Then sort by station

    # Write to csv
    saveCSV(stationFilename, stationData)
