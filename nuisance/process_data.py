# -*- coding: utf-8 -*-

# Data source for Nuisance Flood Levels
# https://tidesandcurrents.noaa.gov/publications/NOAA_Technical_Report_NOS_COOPS_073.pdf

# Data source for Sea Level Rise
# https://tidesandcurrents.noaa.gov/sltrends/sltrends.html

# Data source for water levels (for nuisance flood frequencies)
# https://tidesandcurrents.noaa.gov/inundation/

import argparse
import csv
from datetime import datetime
import inspect
import json
import math
import os
from pprint import pprint
import sys

# add parent directory to sys path to import relative modules
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import lib.mathutils as mu

# input
parser = argparse.ArgumentParser()
parser.add_argument('-sli', dest="SEA_LEVEL_INPUT", default="data/%s_MeanSeaLevelTrends.csv", help="Input sea level data file")
parser.add_argument('-iai', dest="INUNDATION_INPUT", default="data/%s_InundationAnalysis.csv", help="Input inundation analysis data file")
parser.add_argument('-ni', dest="NUISANCE_INPUT", default="data/nuisance_flood_levels.csv", help="Input nuisance flood levels data file")
parser.add_argument('-stations', dest="STATIONS", default="8534720,8575512,8658120,8665530,8670870", help="List of stations")
parser.add_argument('-y0', dest="YEAR_START", type=int, default=1951, help="Year start")
parser.add_argument('-y1', dest="YEAR_END", type=int, default=2015, help="Year end")
parser.add_argument('-data', dest="DATA_FILE", default="data/nuisance.json", help="Path to output data file to cache data")

# init input
args = parser.parse_args()
STATIONS = args.STATIONS.split(",")
YEAR_START = args.YEAR_START
YEAR_END = args.YEAR_END

def readCSV(filename):
    data = []
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            reader = csv.DictReader(f, skipinitialspace=True)
            data = list(reader)
    return data

# read nuisance csv
nuisanceData = readCSV(args.NUISANCE_INPUT)
stationData = {}
for d in nuisanceData:
    stationId = d["St. ID"]
    if stationId in STATIONS:
        stationData[stationId] = {
            "label": d["NOAA Tide Gauge"],
            "nuisanceLevel": float(d["Nuisance Flood Level (above MHHW)"])
        }
print "Retrieved %s stations: %s" % (len(stationData.keys()), stationData.keys())

# Retrieve sea level data
for stationId in STATIONS:
    station = stationData[stationId]
    slrData = readCSV(args.SEA_LEVEL_INPUT % stationId)
    years = {}
    for year in range(YEAR_START, YEAR_END+1):
        years[year] = { "data": [] }
    for d in slrData:
        year = int(d["Year"])
        if year in years.keys():
            value = d["Monthly_MSL"]
            if len(value):
                value = float(value)
                years[year]["data"].append(value)
            # else:
            #     print "Warning: %s at %s-%s has no slr value" % (stationId, year, d["Month"])
    for year in years:
        years[year]["mean"] = mu.mean(years[year]["data"])
        if not len(years[year]["data"]):
            print "Warning: no slr data in station(%s) and year(%s)" % (stationId, year)
    stationData[stationId]["slrData"] = years
print "Processed mean sea level data"

# Retrieve inundation data
for stationId in STATIONS:
    station = stationData[stationId]
    inundationData = readCSV(args.INUNDATION_INPUT % stationId)
    years = {}
    for year in range(YEAR_START, YEAR_END+1):
        years[year] = { "days": [] }
    for d in inundationData:
        dateStart = datetime.strptime(d["Period Start"], '%Y-%m-%d %H:%M')
        dateEnd = datetime.strptime(d["Period End"], '%Y-%m-%d %H:%M')
        year = dateStart.year
        if year >= YEAR_START and dateEnd.year <= YEAR_END:
            value = d["Elevation (Meters) Above Datum"]
            if len(value) and value != "--":
                value = float(value)
                day = dateStart.strftime("%Y-%m-%d")
                if value > station["nuisanceLevel"] and day not in years[year]["days"]:
                    years[year]["days"].append(day)
    for year in years:
        years[year]["dayCount"] = len(years[year]["days"])
    stationData[stationId]["inundationData"] = years
print "Processed inundation data"

# Calculate stats
for stationId in stationData:
    station = stationData[stationId]
    slrData = [d["mean"] for year, d in station["slrData"].iteritems()]
    inundationData = [d["dayCount"] for year, d in station["inundationData"].iteritems()]
    stationData[stationId]["slrRange"] = (min(slrData), max(slrData))
    stationData[stationId]["inundationRange"] = (min(inundationData), max(inundationData))

with open(args.DATA_FILE, 'w') as f:
    json.dump(stationData, f)
    print "Wrote data to %s" % args.DATA_FILE
