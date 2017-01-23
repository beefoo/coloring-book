# -*- coding: utf-8 -*-

# Data source:
# Effects of Climate Change on Global Food Production from SRES Emissions and Socioeconomic Scenarios, v1 (1970 – 2080)
# http://sedac.ciesin.columbia.edu/data/set/crop-climate-effects-climate-global-food-production
# Probabilistic Population Projections based on the World Population Prospects: The 2015 Revision
# https://esa.un.org/unpd/wpp/Download/Probabilistic/Population/

import argparse
import csv
import math
import os
import svgwrite
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-input', dest="INPUT_FILE", default="data/global_food_production_data.csv", help="Path to input data file")
parser.add_argument('-width', dest="WIDTH", type=int, default=800, help="Width of output file")
parser.add_argument('-pad', dest="PAD", type=int, default=100, help="Padding of output file")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/food_production.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
WIDTH = args.WIDTH
PAD = args.PAD

# config
BASELINE_DATA = [
    {"key": "WH_2000", "label": "Wheat production", "description": "Wheat production average 2000 to 2006 (FAO)"},
    {"key": "RI_2000", "label": "Rice production", "description": "Rice production average 2000 to 2006 (FAO)"},
    {"key": "MZ_2000", "label": "Maize production", "description": "Maize production average 2000 to 2006 (FAO)"}
]
# A1 Scenario: more economic focus, globalisation, rapid economic growth, 1.4 - 6.4 °C
# A1FI - An emphasis on fossil-fuels (Fossil Intensive)
PROJECTED_DATA = [
    {"key": "WHA1F2020", "group": "A1F 2020", "baseline": "WH_2000", "label": "Wheat production A1F 2020", "description": "Wheat yield change (%) from baseline under the SRES A1FI 2020 scenario"},
    {"key": "RIA1F2020", "group": "A1F 2020", "baseline": "RI_2000", "label": "Rice production A1F 2020", "description": "Rice yield change (%) from baseline under the SRES A1FI 2020 scenario"},
    {"key": "MZA1F2020", "group": "A1F 2020", "baseline": "MZ_2000", "label": "Maize production A1F 2020", "description": "Maize yield change (%) from baseline under the SRES A1FI 2020 scenario"},
    {"key": "WHA1F2050", "group": "A1F 2050", "baseline": "WH_2000", "label": "Wheat production A1F 2050", "description": "Wheat yield change (%) from baseline under the SRES A1FI 2050 scenario"},
    {"key": "RIA1F2050", "group": "A1F 2050", "baseline": "RI_2000", "label": "Rice production A1F 2050", "description": "Rice yield change (%) from baseline under the SRES A1FI 2050 scenario"},
    {"key": "MZA1F2050", "group": "A1F 2050", "baseline": "MZ_2000", "label": "Maize production A1F 2050", "description": "Maize yield change (%) from baseline under the SRES A1FI 2050 scenario"},
    {"key": "WHA1F2080", "group": "A1F 2080", "baseline": "WH_2000", "label": "Wheat production A1F 2080", "description": "Wheat yield change (%) from baseline under the SRES A1FI 2080 scenario"},
    {"key": "RIA1F2080", "group": "A1F 2080", "baseline": "RI_2000", "label": "Rice production A1F 2080", "description": "Rice yield change (%) from baseline under the SRES A1FI 2080 scenario"},
    {"key": "MZA1F2080", "group": "A1F 2080", "baseline": "MZ_2000", "label": "Maize production A1F 2080", "description": "Maize yield change (%) from baseline under the SRES A1FI 2080 scenario"}
]

def isFloat(string):
    try:
        float(string)
    except ValueError:
        return False
    return True

def readCSV(filename):
    rows = []
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            reader = csv.DictReader(f, skipinitialspace=True)
            rows = list(reader)
    return rows

rows = readCSV(args.INPUT_FILE)
rows.pop() # remove footer

# initialize data
data = []
for i, d in enumerate(BASELINE_DATA):
    baselineKey = d["key"]
    item = d.copy()
    item["value"] = sum([float(row[baselineKey]) for row in rows if isFloat(row[baselineKey])])
    projections = [p for p in PROJECTED_DATA if p["baseline"]==baselineKey]
    pData = []
    for p in projections:
        pitem = p.copy()
        total = 0
        projectionKey = p["key"]
        for row in rows:
            if isFloat(row[baselineKey]) and isFloat(row[projectionKey]):
                total += float(row[baselineKey]) * (float(row[projectionKey])/100 + 1.0)
        pitem["value"] = total
        pitem["percent"] = total / item["value"] - 1.0
        pData.append(pitem)
    item["projections"] = pData
    data.append(item)

# add totals
totals = { "label": "Total Production" }
totals["value"] = sum([d["value"] for d in data])
totalProjections = []
groups = set([p["group"] for p in PROJECTED_DATA])
for groupKey in groups:
    pitem = {"label": "Total production " + groupKey, "group": groupKey}
    pTotal = 0
    for d in data:
        pTotal += sum([p["value"] for p in d["projections"] if p["group"]==groupKey])
    pitem["value"] = pTotal
    pitem["percent"] = pTotal / totals["value"] - 1.0
    totalProjections.append(pitem)
totals["projections"] = totalProjections
data.append(totals)

# print report
for d in data:
    print "%s: %s" % (d["label"], "{:,}".format(d["value"]))
    for p in d["projections"]:
        sign = "+"
        if p["percent"] < 0:
            sign = ""
        print " - %s: %s%s%%" % (p["group"], sign, round(p["percent"]*100, 2))
