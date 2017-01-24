# -*- coding: utf-8 -*-

# Data source:

# Effects of Climate Change on Global Food Production from SRES Emissions and Socioeconomic Scenarios, v1 (1970 – 2080)
# In tons
# http://sedac.ciesin.columbia.edu/data/set/crop-climate-effects-climate-global-food-production

# Probabilistic Population Projections based on the World Population Prospects: The 2015 Revision
# As of July 2015, thousands
# https://esa.un.org/unpd/wpp/Download/Probabilistic/Population/

# Country codes:
# https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes

import argparse
import csv
import math
import os
from pprint import pprint
import svgwrite
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-input', dest="INPUT_FILE", default="data/global_food_production_data.csv", help="Path to input data file")
parser.add_argument('-popest', dest="POPULATION_ESTIMATES", default="data/population_estimates.csv", help="Path to input population estimates data file")
parser.add_argument('-popproj', dest="POPULATION_PROJECTIONS", default="data/population_projections.csv", help="Path to input population projections data file")
parser.add_argument('-width', dest="WIDTH", type=int, default=800, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=int, default=1035, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=int, default=100, help="Padding of output file")
parser.add_argument('-report', dest="REPORT", type=bool, default=False, help="Output report")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/food_production.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
WIDTH = args.WIDTH
HEIGHT = args.HEIGHT
PAD = args.PAD
REPORT = args.REPORT

# config
POPULATION_BASELINE = "2015"
PROJECTIONS = ["2020", "2050", "2080"]
# Baseline data
BASELINE_DATA = [
    {"key": "WH_2000", "label": "Wheat production", "description": "Wheat production average 2000 to 2006 (FAO)"},
    {"key": "RI_2000", "label": "Rice production", "description": "Rice production average 2000 to 2006 (FAO)"},
    {"key": "MZ_2000", "label": "Maize production", "description": "Maize production average 2000 to 2006 (FAO)"}
]
# A1 Scenario: more economic focus, globalisation, rapid economic growth, 1.4 - 6.4 °C
# A1FI - An emphasis on fossil-fuels (Fossil Intensive)
PROJECTED_DATA = [
    {"key": "WHA1F2020", "group": "2020", "baseline": "WH_2000", "label": "Wheat production A1F 2020", "description": "Wheat yield change (%) from baseline under the SRES A1FI 2020 scenario"},
    {"key": "RIA1F2020", "group": "2020", "baseline": "RI_2000", "label": "Rice production A1F 2020", "description": "Rice yield change (%) from baseline under the SRES A1FI 2020 scenario"},
    {"key": "MZA1F2020", "group": "2020", "baseline": "MZ_2000", "label": "Maize production A1F 2020", "description": "Maize yield change (%) from baseline under the SRES A1FI 2020 scenario"},
    {"key": "WHA1F2050", "group": "2050", "baseline": "WH_2000", "label": "Wheat production A1F 2050", "description": "Wheat yield change (%) from baseline under the SRES A1FI 2050 scenario"},
    {"key": "RIA1F2050", "group": "2050", "baseline": "RI_2000", "label": "Rice production A1F 2050", "description": "Rice yield change (%) from baseline under the SRES A1FI 2050 scenario"},
    {"key": "MZA1F2050", "group": "2050", "baseline": "MZ_2000", "label": "Maize production A1F 2050", "description": "Maize yield change (%) from baseline under the SRES A1FI 2050 scenario"},
    {"key": "WHA1F2080", "group": "2080", "baseline": "WH_2000", "label": "Wheat production A1F 2080", "description": "Wheat yield change (%) from baseline under the SRES A1FI 2080 scenario"},
    {"key": "RIA1F2080", "group": "2080", "baseline": "RI_2000", "label": "Rice production A1F 2080", "description": "Rice yield change (%) from baseline under the SRES A1FI 2080 scenario"},
    {"key": "MZA1F2080", "group": "2080", "baseline": "MZ_2000", "label": "Maize production A1F 2080", "description": "Maize yield change (%) from baseline under the SRES A1FI 2080 scenario"}
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
foodData = []
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
    foodData.append(item)

# add totals
totals = { "label": "Total Production" }
totals["value"] = sum([d["value"] for d in foodData])
totalProjections = []
groups = set([p["group"] for p in PROJECTED_DATA])
for groupKey in groups:
    pitem = {"label": "Total production " + groupKey, "group": groupKey}
    pTotal = 0
    for d in foodData:
        pTotal += sum([p["value"] for p in d["projections"] if p["group"]==groupKey])
    pitem["value"] = pTotal
    pitem["percent"] = pTotal / totals["value"] - 1.0
    totalProjections.append(pitem)
totals["projections"] = totalProjections
foodData.append(totals)

# print report
if REPORT:
    for d in foodData:
        print "-----"
        print "%s: %s" % (d["label"], "{:,}".format(int(d["value"])))
        for p in d["projections"]:
            sign = "+"
            if p["percent"] < 0:
                sign = ""
            print " - %s: %s%s%% (%s%s)" % (p["group"], sign, round(p["percent"]*100, 2), sign, "{:,}".format(int(p["value"])-int(d["value"])))

# read population data
rawPopEstimates = readCSV(args.POPULATION_ESTIMATES)
rawPopProjections = readCSV(args.POPULATION_PROJECTIONS)

# baseline population estimates
basePopulation = 0
baseCodes = ["900"]
for e in rawPopEstimates:
    # World population
    if e["Country code"] in baseCodes:
        basePopulation += int(e[POPULATION_BASELINE].replace(" ", "")) * 1000

# population projections
popProjections = {}
for p in rawPopProjections:
    if p["Country code"] in baseCodes:
        for year in PROJECTIONS:
            value = int(p[year].replace(" ", "")) * 1000
            if year in popProjections:
                popProjections[year] += value
            else:
                popProjections[year] = value

# print report
if REPORT:
    print "-----"
    print "Baseline population: %s" % "{:,}".format(basePopulation)
    for year in PROJECTIONS:
        p = popProjections[year]
        percent = round((1.0 * p / basePopulation - 1.0) * 100, 2)
        print " - Projection %s: %s (+%s%%)" % (year, "{:,}".format(p), percent)

# svg config
LABEL_HEIGHT = 50
LABEL_PAD = 10
yearLabels = PROJECTIONS[:]
yearLabelW = 1.0 * WIDTH / len(yearLabels)
dataHeight = (HEIGHT - LABEL_HEIGHT) * 0.5
dataWidth = 0.92 * yearLabelW

# init svg
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
dwgAxis = dwg.g(id="axis")
dwgLabels = dwg.g(id="labels")
dwgData = dwg.g(id="data")

# TODO: define fill patterns

# draw year labels
x = PAD + yearLabelW * 0.5
y = 0.5 * (HEIGHT+PAD*2)
for label in yearLabels:
    dwgLabels.add(dwg.text(label, insert=(x, y), text_anchor="middle", alignment_baseline="middle", font_size=20))
    x += yearLabelW

# draw population data
maxDelta = max([popProjections[year]-basePopulation for year in popProjections])
x = PAD + (yearLabelW-dataWidth) * 0.5
for year in yearLabels:
    delta = popProjections[year]-basePopulation
    ph = 1.0 * delta / maxDelta
    h = ph * dataHeight
    y = dataHeight - h + PAD
    label = int(round(delta / 1000000.0))
    if label >= 1000:
        label = round(delta / 1000000000.0, 1)
        label = "+ " + str(label) + "B people"
    else:
        label = "+ " + str(label) + "M people"
    dwgData.add(dwg.rect(insert=(x, y), size=(dataWidth, h), stroke_width=2, stroke="#000000", fill="none"))
    dwgLabels.add(dwg.text(label, insert=(x+dataWidth*0.5, y-LABEL_PAD), text_anchor="middle", alignment_baseline="after-edge", font_size=20))
    x += yearLabelW

# draw maize production data
food = next((f for f in foodData if "key" in f and f["key"]=="MZ_2000"))
baseTotal = food["value"]
foodProjections = food["projections"]
maxDelta = max([baseTotal-p["value"] for p in foodProjections])
x = PAD + (yearLabelW-dataWidth) * 0.5
y = PAD + dataHeight + LABEL_HEIGHT
for year in yearLabels:
    value = sum([p["value"] for p in foodProjections if p["group"]==year])
    delta = baseTotal - value
    ph = 1.0 * delta / maxDelta
    h = ph * dataHeight
    label = int(round(delta / 1000000.0))
    label = "- " + str(label) + "M tons of corn"
    dwgData.add(dwg.rect(insert=(x, y), size=(dataWidth, h), stroke_width=2, stroke="#000000", fill="none"))
    dwgLabels.add(dwg.text(label, insert=(x+dataWidth*0.5, y+h+LABEL_PAD), text_anchor="middle", alignment_baseline="before-edge", font_size=20))
    x += yearLabelW

# save svg
dwg.add(dwgAxis)
dwg.add(dwgData)
dwg.add(dwgLabels)
dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
