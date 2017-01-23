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

# input
parser = argparse.ArgumentParser()
parser.add_argument('-temperature', dest="TA_FILE", default="data/ocean_temperature_anomalies_188001-201612.csv", help="Path to input temperature anomalies data file")
parser.add_argument('-slr', dest="SLR_FILE", default="data/slr_sla_gbl_free_txj1j2_90.csv", help="Path to input sea level rise data file")
parser.add_argument('-slrh', dest="SLRH_FILE", default="data/CSIRO_Recons_gmsl_mo_2015.csv", help="Path to input sea level rise pre-1993 data file")
# parser.add_argument('-years', dest="YEARS", default="1960,1970,1980,1990,2000,2010,2015", help="Years")
parser.add_argument('-y0', dest="YEAR_START", default=1995, help="Year start")
parser.add_argument('-y1', dest="YEAR_END", default=2015, help="Year end")
parser.add_argument('-yi', dest="YEAR_INCR", default=5, help="Year increment")
parser.add_argument('-width', dest="WIDTH", type=int, default=800, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=int, default=1035, help="Width of output file")
parser.add_argument('-pad', dest="PAD", type=int, default=100, help="Padding of output file")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/ocean.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
YEAR_START = args.YEAR_START
YEAR_END = args.YEAR_END
YEAR_INCR = args.YEAR_INCR
WIDTH = args.WIDTH
HEIGHT = args.HEIGHT
PAD = args.PAD

# config
SLR_KEY_PRIORITY = ["Jason-2", "Jason-1", "TOPEX/Poseidon", "GMSL (mm)"]
COLORS = ["G", "Y", "O", "R", "V"]
AXIS_ROUND_TO_NEAREST = 10
GUIDES = False
LINE_HEIGHT = 50
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
rawSlrhData = readCSV(args.SLRH_FILE)

# pprint(rawTaData[0])
# pprint(rawSlrData[0])
# pprint(rawSlrhData[0])

# normalize date key
for i, d in enumerate(rawSlrhData):
    rawSlrhData[i]["year"] = d["Time"]

# remove any data in non-satellite data after 1993 since more accurate data exists
rawSlrhData = [d for d in rawSlrhData if d["year"] < 1993]

# combine slr data
rawSlrDataCombined = rawSlrData + rawSlrhData

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

# get data ranges
minValue = min([d["slrRange"][0] for d in plotData])
maxValue = max([d["slrRange"][1] for d in plotData])
print "SLR data range: [%s, %s]" % (minValue, maxValue)
axisMin = int(mu.floorToNearest(minValue, AXIS_ROUND_TO_NEAREST))
axisMax = int(mu.ceilToNearest(maxValue, AXIS_ROUND_TO_NEAREST))
print "SLR axis range: [%s, %s]" % (axisMin, axisMax)
taMin = min([d["taRange"][0] for d in plotData])
taMax = max([d["taRange"][1] for d in plotData])
print "TA data range: [%s, %s]" % (taMin, taMax)

# init svg
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
dwgAxis = dwg.g(id="axis")
dwgLabels = dwg.g(id="labels")
dwgData = dwg.g(id="data")
dwgGuides = dwg.g(id="guides")

# draw axis
dwgAxis.add(dwg.rect(insert=(PAD, PAD), size=(WIDTH, HEIGHT), stroke_width=2, stroke="#000000", fill="none"))
axisValue = axisMin + AXIS_ROUND_TO_NEAREST
x = PAD+WIDTH
monthWidth = WIDTH / 12.0
# y axis
while axisValue < axisMax:
    label = str(axisValue) + " mm"
    if axisValue > 0:
        label = "+" + label
    py = mu.norm(axisValue, axisMin, axisMax)
    y = HEIGHT - HEIGHT * py + PAD
    dwgAxis.add(dwg.line(start=(x, y), end=(x + 10, y), stroke_width=2, stroke="#000000"))
    dwgLabels.add(dwg.text(label, insert=(x+15, y), alignment_baseline="middle", font_size=16))
    axisValue += AXIS_ROUND_TO_NEAREST
# x axis
y = PAD + HEIGHT + 10
for month in range(12):
    label = calendar.month_abbr[month+1]
    x = month * monthWidth + monthWidth * 0.5 + PAD
    dwgLabels.add(dwg.text(label, insert=(x, y), text_anchor="middle", alignment_baseline="before-edge", font_size=16))

# draw data
lineDelta = LINE_HEIGHT * 0.5
prevPoints = None
for yi, d in enumerate(plotData):
    points = []
    for month, dm in enumerate(d["months"]):
        x = month * (WIDTH / 11.0) + PAD
        py = mu.norm(dm["slr"], axisMin, axisMax)
        y = HEIGHT - HEIGHT * py + PAD
        points.append((x, y))
        if month <= 0:
            dwgLabels.add(dwg.text(str(d["year"]), insert=(x-10, y), text_anchor="end", alignment_baseline="middle", font_size=16))
    for point in points:
        dwgGuides.add(dwg.circle(center=point, r=3, fill="#000000"))

    # smooth lines
    firstPoint = points[0]
    lastPoint = points[-1]
    points = mu.smoothPoints(points)
    points = [firstPoint] + points + [lastPoint]

    # draw ta data
    for month, dm in enumerate(d["months"]):
        x = month * monthWidth + PAD
        # find intersections
        intersection = mu.xIntersect(points, x)
        y1 = intersection[1]
        y0 = PAD + HEIGHT
        if prevPoints is not None:
            intersection = mu.xIntersect(prevPoints, x)
            y0 = intersection[1]
        # draw divider lines
        if month > 0:
            dwgData.add(dwg.line(start=(x, y0-6), end=(x, y1+6), stroke_width=2, stroke="#000000", stroke_dasharray="5,2"))
        # draw color label
        pt = mu.norm(dm["ta"], taMin, taMax)
        ci = min(int(pt * colorCount), colorCount-1)
        color = COLORS[ci]
        xc = x + monthWidth * 0.5
        yc = y1 + (y0 - y1) * 0.5
        dwgLabels.add(dwg.text(color, insert=(xc, yc), text_anchor="middle", alignment_baseline="middle", font_size=16))

    # make lines
    dwgData.add(dwg.polyline(points=points, stroke_width=2, stroke="#000000", fill="none"))

    # pathCurve = pointsToCurve(points)
    # dwgData.add(dwg.path(d=pathCurve, stroke_width=2, stroke="#000000", fill="none"))

    prevPoints = points[:]

# save svg
dwg.add(dwgAxis)
dwg.add(dwgData)
dwg.add(dwgLabels)
if GUIDES:
    dwg.add(dwgGuides)
dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
