# -*- coding: utf-8 -*-

# Data Sources

# Sea level rise:
# https://www.star.nesdis.noaa.gov/sod/lsa/SeaLevelRise/LSA_SLR_timeseries_global.php (Satellite sea level observations 1993-2015)
# http://www.cmar.csiro.au/sealevel/sl_data_cmar.html (Coastal tide gauge records 1880-2012)

# Ocean temperature:
# https://www.ncdc.noaa.gov/monitoring-references/faq/anomalies.php

# Ocean acidification:
# http://hahana.soest.hawaii.edu/hot/products/products.html
# https://www.epa.gov/climate-indicators/climate-change-indicators-ocean-acidity

import argparse
import calendar
import csv
from datetime import datetime
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

import lib.mathutils as mu
import lib.svgutils as svgu

# input
parser = argparse.ArgumentParser()
parser.add_argument('-temperature', dest="TA_FILE", default="data/ocean_temperature_anomalies_188001-201612.csv", help="Path to input temperature anomalies data file")
parser.add_argument('-slr', dest="SLR_FILE", default="data/slr_sla_gbl_free_txj1j2_90.csv", help="Path to input sea level rise data file")
parser.add_argument('-slrh', dest="SLRH_FILE", default="data/CSIRO_Recons_gmsl_mo_2015.csv", help="Path to input sea level rise pre-1993 data file")
# parser.add_argument('-years', dest="YEARS", default="1960,1970,1980,1990,2000,2010,2015", help="Years")
parser.add_argument('-y0', dest="YEAR_START", default=1995, help="Year start")
parser.add_argument('-y1', dest="YEAR_END", default=2015, help="Year end")
parser.add_argument('-yi', dest="YEAR_INCR", default=5, help="Year increment")
parser.add_argument('-width', dest="WIDTH", type=float, default=8.5, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=float, default=11, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=float, default=0.5, help="Padding of output file")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/ocean.svg", help="Path to output svg file")
parser.add_argument('-guides', dest="GUIDES", type=bool, default=False, help="Show guides")
parser.add_argument('-report', dest="REPORT", type=bool, default=False, help="Print report")

# init input
args = parser.parse_args()
DPI = 72
PAD = args.PAD * DPI
WIDTH = args.WIDTH * DPI - PAD * 2
HEIGHT = args.HEIGHT * DPI - PAD * 2
YEAR_START = args.YEAR_START
YEAR_END = args.YEAR_END
YEAR_INCR = args.YEAR_INCR
GUIDES = args.GUIDES

# chart config
Y_LEFT_WIDTH = 0.55 * DPI
Y_RIGHT_WIDTH = 0.725 * DPI
Y_WIDTH = Y_LEFT_WIDTH + Y_RIGHT_WIDTH
X_HEIGHT = 0.375 * DPI
CHART_WIDTH = WIDTH - Y_WIDTH
CHART_HEIGHT = HEIGHT - X_HEIGHT
CHART_OFFSET_X = PAD + Y_LEFT_WIDTH
CHART_OFFSET_Y = PAD
DATA_CURVE_WIDTH = 3

# config
SLR_KEY_PRIORITY = ["Jason-2", "Jason-1", "TOPEX/Poseidon", "GMSL (mm)"]
COLORS = ["B", "G", "Y", "O", "R", "V"]
AXIS_ROUND_TO_NEAREST = 10
colorCount = len(COLORS)

def parseNumber(string):
    try:
        num = float(string)
        if "." not in string:
            num = int(string)
        return num
    except ValueError:
        return None

def parseNumbers(arr):
    for i, item in enumerate(arr):
        for key in item:
            arr[i][key] = parseNumber(item[key])
    return arr

def pointsToCurve(points):
    first = points.pop(0)
    curve = "M%s %s" % first
    for i, point in enumerate(points):
        if i % 2 > 0:
            p0 = points[i-1]
            p1 = point
            curve += " Q %s %s, %s %s" % (p0[0], p0[1], p1[0], p1[1])
    if len(points) % 2 > 0:
        curve += " T %s %s" % points[-1]
    return curve

def readCSV(filename):
    rows = []
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            lines = [line for line in f if not line.startswith("#")]
            reader = csv.DictReader(lines, skipinitialspace=True)
            rows = list(reader)
            rows = parseNumbers(rows)
    return rows

rawTaData = readCSV(args.TA_FILE)
rawSlrData = readCSV(args.SLR_FILE)

# use pre-1993 data if configured as such
if YEAR_START < 1993:
    rawSlrhData = readCSV(args.SLRH_FILE)

    # normalize date key
    for i, d in enumerate(rawSlrhData):
        rawSlrhData[i]["year"] = d["Time"]

    # remove any data in non-satellite data after 1993 since more accurate data exists
    rawSlrhData = [d for d in rawSlrhData if d["year"] < 1993]

    # combine slr data
    rawSlrDataCombined = rawSlrData + rawSlrhData
else:
    rawSlrDataCombined = rawSlrData + []

# do some normalization
for i, d in enumerate(rawSlrDataCombined):
    # break month out of year
    year = int(d["year"])
    rawSlrDataCombined[i]["yearMonth"] = d["year"]
    rawSlrDataCombined[i]["month"] = int((d["year"] - year) * 12.0)
    rawSlrDataCombined[i]["year"] = year
    # choose a value
    value = None
    for k in SLR_KEY_PRIORITY:
        if k in d and d[k] is not None:
            value = d[k]
            break
    rawSlrDataCombined[i]["value"] = value

# more normalization
for i, d in enumerate(rawTaData):
    # break month out of year
    date = datetime.strptime(str(d["Year"]), "%Y%m").date()
    rawTaData[i]["yearMonth"] = d["Year"]
    rawTaData[i]["month"] = date.month - 1
    rawTaData[i]["year"] = date.year

# group by years, aggregate by monthly mean
plotData = []
year = YEAR_START
while year <= YEAR_END:
    months = []
    for month in range(12):
        meanSlrValue = mu.mean([d["value"] for d in rawSlrDataCombined if d["month"]==month and d["year"]==year])
        meanTaValue = mu.mean([d["Value"] for d in rawTaData if d["month"]==month and d["year"]==year])
        months.append({
            "slr": meanSlrValue,
            "ta": meanTaValue
        })
    slrValues = [m["slr"] for m in months]
    taValues = [m["ta"] for m in months]
    plotData.append({
        "year": year,
        "months": months,
        "slrRange": (min(slrValues), max(slrValues)),
        "taRange": (min(taValues), max(taValues))
    })
    year += YEAR_INCR
plotData = sorted(plotData, key=lambda p: p["year"])

# determine what value should be "zero" on the y-axis (SLR) -> mean of first year
slrZeroValue = mu.mean([m["slr"] for m in plotData[0]["months"]])
# normalize slr values to zero value
for i,p in enumerate(plotData):
    for j,m in enumerate(p["months"]):
        plotData[i]["months"][j]["slr"] = m["slr"] - slrZeroValue
    slrr = p["slrRange"]
    plotData[i]["slrRange"] = (slrr[0]-slrZeroValue, slrr[1]-slrZeroValue)

# get data ranges
minValue = min([d["slrRange"][0] for d in plotData])
maxValue = max([d["slrRange"][1] for d in plotData])
print "SLR data range: [%s, %s]" % (minValue, maxValue)
axisMin = int(mu.floorToNearest(minValue, AXIS_ROUND_TO_NEAREST))
axisMax = int(mu.roundToNearest(maxValue, AXIS_ROUND_TO_NEAREST))
print "SLR axis range: [%s, %s]" % (axisMin, axisMax)
taMin = min([d["taRange"][0] for d in plotData])
taMax = max([d["taRange"][1] for d in plotData])
print "TA data range (°C): [%s, %s]" % (taMin, taMax)

if args.REPORT:
    tafMin = taMin * 1.8
    tafMax = taMax * 1.8
    taStep = tafMax / colorCount
    print "TA data range (°F): [%s, %s]" % (tafMin, tafMax)
    vf = 0
    for i,c in enumerate(COLORS):
        print "%s: %s to %s°F" % (c, vf, vf+taStep)
        vf += taStep
    sys.exit(1)

# init svg
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
dwgAxis = dwg.g(id="axis")
dwgLabels = dwg.g(id="labels")
dwgData = dwg.g(id="data")
dwgGuides = dwg.g(id="guides")

# draw axis
axisValue = axisMin + AXIS_ROUND_TO_NEAREST
x = PAD+WIDTH-Y_RIGHT_WIDTH
monthWidth = (CHART_WIDTH) / 12.0
# y axis
while axisValue < axisMax:
    label = str(axisValue)
    if axisValue > 0:
        label = "+" + label
    py = mu.norm(axisValue, axisMin, axisMax)
    y = CHART_HEIGHT - CHART_HEIGHT * py + PAD
    dwgAxis.add(dwg.line(start=(x, y), end=(x+5, y), stroke_width=2, stroke="#000000"))
    dwgLabels.add(dwg.text(label, insert=(x+10, y), alignment_baseline="middle", font_size=14))
    axisValue += AXIS_ROUND_TO_NEAREST
# draw y axis label
yAxisLabelRight = "Change in mean sea level (mm)"
labelX = PAD+WIDTH-7
labelY = PAD+CHART_HEIGHT*0.4
dwgLabels.add(dwg.text(yAxisLabelRight, insert=(labelX, labelY), alignment_baseline="middle", font_size=14, dominant_baseline="central", transform="rotate(90,%s,%s)" % (labelX, labelY)))
# x axis
y = PAD + HEIGHT - X_HEIGHT + X_HEIGHT * 0.5
for month in range(12):
    label = calendar.month_abbr[month+1]
    x = month * monthWidth + monthWidth * 0.5 + PAD + Y_LEFT_WIDTH
    dwgLabels.add(dwg.text(label, insert=(x, y), text_anchor="middle", alignment_baseline="middle", font_size=14))

# draw data
prevPoints = None
prevIntersections = None
prevIntersectionsC = None
for yi, d in enumerate(plotData):
    points = []
    for month, dm in enumerate(d["months"]):
        x = month * (CHART_WIDTH / 11.0) + CHART_OFFSET_X
        py = mu.norm(dm["slr"], axisMin, axisMax)
        y = CHART_HEIGHT - CHART_HEIGHT * py + PAD
        points.append((x, y))
        if month <= 0:
            dwgLabels.add(dwg.text(str(d["year"]), insert=(CHART_OFFSET_X-10, y), text_anchor="end", alignment_baseline="middle", font_size=14))
    for point in points:
        dwgGuides.add(dwg.circle(center=point, r=3, fill="#000000"))

    # init prev intersections
    if prevIntersections is None:
        prevIntersections = []
        prevIntersectionsC = []
        for month, dm in enumerate(d["months"]):
            x = month * monthWidth + CHART_OFFSET_X
            y = PAD + CHART_HEIGHT
            prevIntersections.append((x, y))
            prevIntersectionsC.append((x+0.5*monthWidth, y))

    # retrieve intersections
    intersections = []
    intersectionsC = []
    for month, dm in enumerate(d["months"]):
        x = month * monthWidth + CHART_OFFSET_X
        # find intersections
        intersection = mu.xIntersect(points, x)
        intersections.append((x, intersection[1]))
        # find intersections at center
        xc = x+0.5*monthWidth
        intersectionC = mu.xIntersect(points, xc)
        intersectionsC.append((xc, intersectionC[1]))

    # draw ta data
    for month, dm in enumerate(d["months"]):
        x = month * monthWidth + CHART_OFFSET_X
        y1 = intersections[month][1]
        y0 = prevIntersections[month][1]

        # draw divider lines
        if month > 0:
            dwgData.add(dwg.line(start=(x, y0-6), end=(x, y1+6), stroke_width=1, stroke="#000000", stroke_dasharray="3,1"))

        # draw color label
        pt = mu.norm(dm["ta"], 0, taMax)
        ci = min(int(pt * colorCount), colorCount-1)
        color = COLORS[ci]
        y1 = intersectionsC[month][1]
        y0 = prevIntersectionsC[month][1]
        xc = x + monthWidth * 0.5
        yc = y1 + (y0 - y1) * 0.5
        dwgLabels.add(dwg.text(color, insert=(xc, yc), text_anchor="middle", alignment_baseline="middle", font_size=14))

    pathCurve = svgu.pointsToCurve(points)
    dwgData.add(dwg.path(d=pathCurve, stroke_width=DATA_CURVE_WIDTH, stroke="#000000", fill="none"))

    prevPoints = points[:]
    prevIntersections = intersections[:]
    prevIntersectionsC = intersectionsC[:]

y = CHART_HEIGHT + PAD
p0 = prevPoints[0]
p1 = prevPoints[-1]
offset = DATA_CURVE_WIDTH * 0.5
dwgAxis.add(dwg.polyline(points=[(p0[0], p0[1]-offset), (CHART_OFFSET_X, y), (CHART_OFFSET_X+CHART_WIDTH, y), (p1[0], p1[1]-offset)], stroke_width=2, stroke="#000000", fill="none"))

# save svg
dwg.add(dwgAxis)
dwg.add(dwgData)
dwg.add(dwgLabels)
dwg.add(dwg.rect(insert=(PAD,PAD), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))
if GUIDES:
    dwg.add(dwgGuides)
dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
