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
import svgwrite
import sys

# add parent directory to sys path to import relative modules
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import lib.mathutils as mu

# input
parser = argparse.ArgumentParser()
parser.add_argument('-in', dest="INPUT_FILE", default="data/nuisance.json", help="Input nuisance flooding data file")
parser.add_argument('-width', dest="WIDTH", type=int, default=800, help="Year start")
parser.add_argument('-height', dest="HEIGHT", type=int, default=1000, help="Year start")
parser.add_argument('-pad', dest="PAD", type=int, default=200, help="Year start")
parser.add_argument('-stations', dest="STATIONS", default="8575512,8658120,8665530", help="List of stations")
parser.add_argument('-y0', dest="YEAR_START", type=int, default=1951, help="Year start")
parser.add_argument('-y1', dest="YEAR_END", type=int, default=2015, help="Year end")
parser.add_argument('-out', dest="OUTPUT_FILE", default="data/inundation.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
WIDTH = args.WIDTH
HEIGHT = args.HEIGHT
PAD = args.PAD
STATIONS = args.STATIONS.split(",")
YEAR_START = args.YEAR_START
YEAR_END = args.YEAR_END

# config
YEAR_LABELS_WIDTH = 80
YEAR_TICK_WIDTH = 15
YEAR_LABEL_INCREMENT = 5
VALUE_TICK_WIDTH = 20
VALUE_TICK_HEIGHT = 20
SLR_LABELS = [
    {"value": 0.127, "label": "5''"},
    {"value": 0.254, "label": "10''"}
]
INUNDATION_LABELS = [
    {"value": 20, "label": "20"},
    {"value": 40, "label": "40"},
    {"value": 60, "label": "60"},
    {"value": 80, "label": "80"}
]
DASHARRAYS = [None, [5, 2], [2]]
AXIS_STROKE_WIDTH = 2
DATA_STROKE_WIDTH = 3

stationData = {}
with open(args.INPUT_FILE) as f:
    d = json.load(f)
    for stationId in STATIONS:
        stationData[stationId] = d["stationData"][stationId]

# Init svg
width = WIDTH+PAD*2
height = HEIGHT+PAD*2
cx = width * 0.5
cy = height * 0.5
axisW = (WIDTH - YEAR_LABELS_WIDTH) * 0.5
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(width, height), profile='full')
dwgLabels = dwg.g(id="labels")
dwgAxis = dwg.g(id="axis")

# Draw year labels
dwgYears = dwg.g(id="years")
year = YEAR_START
x = cx
y = PAD
yearLabelCount = (YEAR_END - YEAR_START + 1) / YEAR_LABEL_INCREMENT + 1
dy = 1.0 * HEIGHT / (yearLabelCount-1)
for i in range(yearLabelCount):
    yearText = str(year - 1)
    # ticks
    dwgAxis.add(dwg.line(start=(axisW + PAD, y), end=(axisW + PAD + YEAR_TICK_WIDTH, y), stroke="#000000", stroke_width=AXIS_STROKE_WIDTH))
    dwgAxis.add(dwg.line(start=(axisW + PAD + YEAR_LABELS_WIDTH - YEAR_TICK_WIDTH, y), end=(axisW + PAD + YEAR_LABELS_WIDTH, y), stroke="#000000", stroke_width=AXIS_STROKE_WIDTH))
    # year
    dwgLabels.add(dwg.text(yearText, insert=(x, y), text_anchor="middle", alignment_baseline="middle", font_size=20))
    year += YEAR_LABEL_INCREMENT
    y += dy

# SLR axis
dwgAxis.add(dwg.line(start=(axisW + PAD, PAD), end=(axisW + PAD, HEIGHT + PAD), id="slr-x-axis", stroke="#000000", stroke_width=AXIS_STROKE_WIDTH))
dwgAxis.add(dwg.line(start=(PAD, HEIGHT + PAD), end=(axisW + PAD, HEIGHT + PAD), id="slr-y-axis", stroke="#000000", stroke_width=AXIS_STROKE_WIDTH))
# Draw ticks
minValue = min([d["slrRange"][0] for k, d in stationData.iteritems()])
maxValue = max([d["slrRange"][1] for k, d in stationData.iteritems()])
print "SLR Range: [%s, %s]" % (minValue, maxValue)
y = HEIGHT + PAD
for label in SLR_LABELS:
    p = mu.norm(label["value"], minValue, maxValue)
    x = PAD + axisW - p * axisW
    x1 = x+VALUE_TICK_WIDTH
    y1 = y+VALUE_TICK_HEIGHT
    dwgAxis.add(dwg.line(start=(x, y), end=(x1, y1), stroke="#000000", stroke_width=AXIS_STROKE_WIDTH))
    dwgLabels.add(dwg.text(label["label"], insert=(x1, y1), alignment_baseline="before-edge", font_size=20))
# Draw data
dwgSLR = dwg.g(id="slr")
for i, stationId in enumerate(STATIONS):
    station = stationData[stationId]
    dashArray = DASHARRAYS[i % len(DASHARRAYS)]
    data = station["slrData"]
    points = []
    for d in data:
        value = d["value"]
        if value >= 0:
            py = mu.norm(d["year"], YEAR_START, YEAR_END)
            y = PAD + py * HEIGHT
            px = mu.norm(value, minValue, maxValue)
            x = PAD + axisW - px * axisW
            points.append((x,y))
    points = mu.smoothPoints(points)
    # close points
    points.insert(0, (PAD+axisW, PAD))
    points.append((points[-1][0], PAD+HEIGHT))
    line = dwg.polyline(points=points, stroke="#000000", stroke_width=DATA_STROKE_WIDTH, fill="none")
    if dashArray:
        line.dasharray(dashArray)
    dwgSLR.add(line)

# Inundation axis
dwgAxis.add(dwg.line(start=(axisW + PAD + YEAR_LABELS_WIDTH, PAD), end=(axisW + PAD + YEAR_LABELS_WIDTH, HEIGHT + PAD), id="inundation-x-axis", stroke="#000000", stroke_width=AXIS_STROKE_WIDTH))
dwgAxis.add(dwg.line(start=(axisW + PAD + YEAR_LABELS_WIDTH, HEIGHT + PAD), end=(WIDTH + PAD, HEIGHT + PAD), id="inundation-y-axis", stroke="#000000", stroke_width=AXIS_STROKE_WIDTH))
# Draw ticks
minValue = min([d["inundationRange"][0] for k, d in stationData.iteritems()])
maxValue = max([d["inundationRange"][1] for k, d in stationData.iteritems()])
print "Inundation Range: [%s, %s]" % (minValue, maxValue)
y = HEIGHT + PAD
for label in INUNDATION_LABELS:
    p = mu.norm(label["value"], minValue, maxValue)
    x = PAD + axisW + YEAR_LABELS_WIDTH + p * axisW
    x1 = x-VALUE_TICK_WIDTH
    y1 = y+VALUE_TICK_HEIGHT
    dwgAxis.add(dwg.line(start=(x, y), end=(x1, y1), stroke="#000000", stroke_width=AXIS_STROKE_WIDTH))
    dwgLabels.add(dwg.text(label["label"], insert=(x1, y1), text_anchor="end", alignment_baseline="before-edge", font_size=20))
# Draw data
dwgInundation = dwg.g(id="inundation")
for i, stationId in enumerate(STATIONS):
    station = stationData[stationId]
    dashArray = DASHARRAYS[i % len(DASHARRAYS)]
    data = station["inundationData"]
    points = []
    for d in data:
        py = mu.norm(d["year"], YEAR_START, YEAR_END)
        y = PAD + py * HEIGHT
        px = mu.norm(d["value"], minValue, maxValue)
        x = PAD + axisW + YEAR_LABELS_WIDTH + px * axisW
        points.append((x,y))
    points = mu.smoothPoints(points)
    # close points
    points.insert(0, (PAD+axisW+YEAR_LABELS_WIDTH, PAD))
    points.append((points[-1][0], PAD+HEIGHT))
    line = dwg.polyline(points=points, stroke="#000000", stroke_width=DATA_STROKE_WIDTH, fill="none")
    if dashArray:
        line.dasharray(dashArray)
    dwgInundation.add(line)

# Save svg
dwg.add(dwgYears)
dwg.add(dwgSLR)
dwg.add(dwgInundation)
dwg.add(dwgAxis)
dwg.add(dwgLabels)
dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
