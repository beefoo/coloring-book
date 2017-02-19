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
import inspect
import math
import os
from pprint import pprint
import svgwrite
import sys

# add parent directory to sys path to import relative modules
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import lib.svgutils as svgu

# input
parser = argparse.ArgumentParser()
parser.add_argument('-input', dest="INPUT_FILE", default="data/global_food_production_data.csv", help="Path to input data file")
parser.add_argument('-popest', dest="POPULATION_ESTIMATES", default="data/population_estimates.csv", help="Path to input population estimates data file")
parser.add_argument('-popproj', dest="POPULATION_PROJECTIONS", default="data/population_projections.csv", help="Path to input population projections data file")
parser.add_argument('-width', dest="WIDTH", type=int, default=8.5, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=int, default=11.0, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=int, default=0.5, help="Padding of output file")
parser.add_argument('-report', dest="REPORT", type=bool, default=False, help="Output report")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/food_production.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
DPI = 72
PAD = args.PAD * DPI
WIDTH = args.WIDTH * DPI - PAD * 2
HEIGHT = args.HEIGHT * DPI - PAD * 2
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
LABEL_HEIGHT = 0.25 * DPI
YEAR_LABEL_HEIGHT = 0.5 * DPI
LABEL_PAD = 0.1 * DPI
yearLabels = PROJECTIONS[:]
yearLabelW = 1.0 * WIDTH / len(yearLabels)
dataHeight = (HEIGHT - YEAR_LABEL_HEIGHT - LABEL_HEIGHT * 2 - LABEL_PAD * 2) * 0.5
dataWidth = 0.833 * yearLabelW
arrowHeight = 0.4 * DPI
arrowWidth = yearLabelW
xOffset = 0.5 * (arrowWidth - dataWidth)
yOffset = arrowHeight

# init svg
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
dwgAxis = dwg.g(id="axis")
dwgLabels = dwg.g(id="labels")
dwgData = dwg.g(id="data")

# define people pattern
personH = 40
patternSpace = 3
svgMan = svgu.getDataFromSVG("svg/man.svg")
svgWoman = svgu.getDataFromSVG("svg/woman.svg")
manScale = 1.0 * personH / svgMan["height"]
womanScale = 1.0 * personH / svgWoman["height"]
manWidth = svgMan["width"] * manScale
womanWidth = svgWoman["width"] * womanScale
personW = max(manWidth, womanWidth)
patternW = personW * 2 + patternSpace * 2
patternH = personH + patternSpace
personPatternDef = dwg.pattern(id="people", patternUnits="userSpaceOnUse", size=(patternW, patternH), patternTransform="rotate(45)")
for path in svgMan["paths"]:
    strokeWidth = 1.0
    hw = svgMan["width"] * 0.5
    hh = svgMan["height"] * 0.5
    personPatternDef.add(dwg.path(d=path, transform="scale(%s) rotate(180,%s,%s)" % (manScale, hw, hh), stroke_width=strokeWidth, stroke="#000000", fill="none"))
for path in svgWoman["paths"]:
    strokeWidth = 1.0
    x = personW + patternSpace
    y = personH * 0.5 + patternSpace * 0.5
    personPatternDef.add(dwg.path(d=path, transform="translate(%s, %s) scale(%s)" % (x, y, womanScale), stroke_width=strokeWidth, stroke="#000000", fill="none"))
    y = -1 * (patternH - y)
    personPatternDef.add(dwg.path(d=path, transform="translate(%s, %s) scale(%s)" % (x, y, womanScale), stroke_width=strokeWidth, stroke="#000000", fill="none"))
dwg.defs.add(personPatternDef)

# define corn pattern
cornH = 40
patternSpace = 3
svgCorn = svgu.getDataFromSVG("svg/corn_02.svg")
scale = 1.0 * personH / svgCorn["height"]
cornW = svgCorn["width"] * scale
patternW = cornW * 2 + patternSpace * 2
patternH = cornH + patternSpace
cornPatternDef = dwg.pattern(id="corn", patternUnits="userSpaceOnUse", size=(patternW, patternH), patternTransform="rotate(135)")
for path in svgCorn["paths"]:
    strokeWidth = 1.2
    hw = svgCorn["width"] * 0.5
    hh = svgCorn["height"] * 0.5
    # t = svgu.getTransformString(w, h, x, y, sx=1, sy=1, r=0)
    cornPatternDef.add(dwg.path(d=path, transform="scale(%s) rotate(180,%s,%s)" % (scale, hw, hh), stroke_width=strokeWidth, stroke="#000000", fill="none"))
    x = cornW + patternSpace
    y = cornH * 0.5 + patternSpace * 0.5
    cornPatternDef.add(dwg.path(d=path, transform="translate(%s, %s) scale(%s)" % (x, y, scale), stroke_width=strokeWidth, stroke="#000000", fill="none"))
    y = -1 * (patternH - y)
    cornPatternDef.add(dwg.path(d=path, transform="translate(%s, %s) scale(%s)" % (x, y, scale), stroke_width=strokeWidth, stroke="#000000", fill="none"))
dwg.defs.add(cornPatternDef)

# draw year labels
x = PAD + yearLabelW * 0.5
cy = 0.5 * (HEIGHT+PAD*2)
y = cy
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
    y = dataHeight - h + PAD + LABEL_HEIGHT + LABEL_PAD
    label = int(round(delta / 1000000.0))
    if label >= 1000:
        label = round(delta / 1000000000.0, 1)
        label = "+ " + str(label) + "B people"
    else:
        label = "+ " + str(label) + "M people"

    # draw arrow
    p1 = (x+dataWidth*0.5, y)
    # p2 = (x-xOffset, y+yOffset)
    p3 = (x, y+yOffset)
    p4 = (x, y+h)
    p5 = (x+dataWidth, y+h)
    p6 = (x+dataWidth, y+yOffset)
    # p7 = (x+dataWidth+xOffset, y+yOffset)
    arrow = [p1, p3, p4, p5, p6]

    dwgData.add(dwg.polygon(points=arrow, stroke="#000000", stroke_width=2, fill="url(#people)"))
    dwgLabels.add(dwg.text(label, insert=(x+dataWidth*0.5, y-LABEL_PAD), text_anchor="middle", alignment_baseline="after-edge", font_size=20))
    x += yearLabelW

# draw maize production data
food = next((f for f in foodData if "key" in f and f["key"]=="MZ_2000"))
baseTotal = food["value"]
foodProjections = food["projections"]
maxDelta = max([baseTotal-p["value"] for p in foodProjections])
x = PAD + (yearLabelW-dataWidth) * 0.5
y = PAD + dataHeight + LABEL_HEIGHT + YEAR_LABEL_HEIGHT + LABEL_PAD
for year in yearLabels:
    value = sum([p["value"] for p in foodProjections if p["group"]==year])
    delta = baseTotal - value
    ph = 1.0 * delta / maxDelta
    h = ph * dataHeight
    label = int(round(delta / 1000000.0))
    label = "- " + str(label) + "M tons of corn"

    # draw arrow
    p1 = (x+dataWidth*0.5, y+h)
    # p2 = (x-xOffset, y+h-yOffset)
    p3 = (x, y+h-yOffset)
    p4 = (x, y)
    p5 = (x+dataWidth, y)
    p6 = (x+dataWidth, y+h-yOffset)
    # p7 = (x+dataWidth+xOffset, y+h-yOffset)
    arrow = [p1, p3, p4, p5, p6]

    dwgData.add(dwg.polygon(points=arrow, stroke="#000000", stroke_width=2, fill="url(#corn)"))
    dwgLabels.add(dwg.text(label, insert=(x+dataWidth*0.5, y+h+LABEL_PAD), text_anchor="middle", alignment_baseline="before-edge", font_size=20))
    x += yearLabelW

# save svg
dwg.add(dwgAxis)
dwg.add(dwgData)
dwg.add(dwgLabels)
dwg.add(dwg.rect(insert=(PAD,PAD), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))

dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
