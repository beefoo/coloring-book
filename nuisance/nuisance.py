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
parser.add_argument('-width', dest="WIDTH", type=float, default=8.5, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=float, default=11, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=float, default=0.5, help="Padding of output file")
parser.add_argument('-stations', dest="STATIONS", default="8658120,8575512,8665530", help="List of stations")
parser.add_argument('-y0', dest="YEAR_START", type=int, default=1951, help="Year start")
parser.add_argument('-y1', dest="YEAR_END", type=int, default=2015, help="Year end")
parser.add_argument('-out', dest="OUTPUT_FILE", default="data/nuisance.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
DPI = 72
PAD = args.PAD * DPI
WIDTH = args.WIDTH * DPI - PAD * 2
HEIGHT = args.HEIGHT * DPI - PAD * 2
STATIONS = args.STATIONS.split(",")
YEAR_START = args.YEAR_START
YEAR_END = args.YEAR_END
LABEL_WIDTH_LEFT = 0.425 * DPI
LABEL_WIDTH_RIGHT = 0.625 * DPI
LABEL_WIDTH = LABEL_WIDTH_LEFT + LABEL_WIDTH_RIGHT
MARGIN = 0.333 * DPI
TICK_WIDTH = 0.1 * DPI

SLR_LABELS = [
    {"value": 0.127, "label": "5''"},
    {"value": 0.254, "label": "10''"}
]
INUNDATION_LABELS = [
    {"value": 40, "label": "40"},
    {"value": 80, "label": "80"}
]

stationData = {}
with open(args.INPUT_FILE) as f:
    d = json.load(f)
    for stationId in STATIONS:
        stationData[stationId] = d["stationData"][stationId]

# Calculations
offsetY = PAD
offsetX = PAD
width = WIDTH+PAD*2
height = HEIGHT+PAD*2
stationHeight = 1.0 * (HEIGHT-MARGIN*(len(STATIONS)-1)) / len(STATIONS)
dataWidth = WIDTH - LABEL_WIDTH
dataHeight = stationHeight * 0.5
yearCount = YEAR_END - YEAR_START + 1
minSlrValue = min([d["slrRange"][0] for k, d in stationData.iteritems()])
maxSlrValue = max([d["slrRange"][1] for k, d in stationData.iteritems()])
minInundValue = min([d["inundationRange"][0] for k, d in stationData.iteritems()])
maxInundValue = max([d["inundationRange"][1] for k, d in stationData.iteritems()])

# Init svg
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(width, height), profile='full')
dwgLabels = dwg.add(dwg.g(id="labels"))
dwgAxis = dwg.add(dwg.g(id="axis"))
dwgData = dwg.add(dwg.g(id="data"))

y = offsetY
for i, stationId in enumerate(STATIONS):
    station = stationData[stationId]
    hy = y + stationHeight * 0.5
    x = offsetX

    # draw labels
    labelPad = 3
    labelX = x+LABEL_WIDTH_LEFT-labelPad
    labelY = hy
    dwgLabels.add(dwg.text(str(YEAR_START-1), insert=(labelX, labelY), text_anchor="end", alignment_baseline="middle", font_size=12))
    labelX = x+LABEL_WIDTH_LEFT+dataWidth+labelPad
    dwgLabels.add(dwg.text(str(YEAR_END), insert=(labelX, labelY), text_anchor="start", alignment_baseline="middle", font_size=12))
    x += LABEL_WIDTH_LEFT

    if i <= 0:
        labelX = x + dataWidth + LABEL_WIDTH_RIGHT
        labelY = hy - stationHeight * 0.25
        dwgLabels.add(dwg.text("Mean sea level rise", insert=(labelX, labelY), text_anchor="middle", alignment_baseline="before-edge", font_size=12, dominant_baseline="central", transform="rotate(90,%s,%s)" % (labelX, labelY)))
        labelY = hy + stationHeight * 0.25
        dwgLabels.add(dwg.text("Days of flooding", insert=(labelX, labelY), text_anchor="middle", alignment_baseline="before-edge", font_size=12, dominant_baseline="central", transform="rotate(90,%s,%s)" % (labelX, labelY)))

    # draw station
    dwgLabels.add(dwg.text(station["label"], insert=(x, y), alignment_baseline="before-edge", font_size=16))

    # draw axis
    dwgAxis.add(dwg.line(start=(x, hy), end=(x+dataWidth, hy), stroke="#000000", stroke_width=1, stroke_dasharray="3,1"))

    # draw slr data
    dw = dataWidth / yearCount
    points = [(x, hy)]
    for d in station["slrData"]:
        px = mu.norm(d["year"], YEAR_START, YEAR_END+1)
        py = max(mu.norm(d["value"], minSlrValue, maxSlrValue), 0)
        dx = x + px * dataWidth
        dy = hy - py * dataHeight
        points.append((dx, dy))
        points.append((dx+dw, dy))
        dwgData.add(dwg.line(start=(dx+dw, hy), end=(dx+dw, dy), stroke="#000000", stroke_width=1))
    points.append((x+dataWidth, hy))
    dwgData.add(dwg.polyline(points=points, stroke="#000000", stroke_width=1.5, fill="none"))

    # draw inundation data
    points = [(x, hy)]
    for d in station["inundationData"]:
        px = mu.norm(d["year"], YEAR_START, YEAR_END+1)
        py = max(mu.norm(d["value"], minInundValue, maxInundValue), 0)
        dx = x + px * dataWidth
        dy = hy + py * dataHeight
        points.append((dx, dy))
        points.append((dx+dw, dy))
        dwgData.add(dwg.line(start=(dx+dw, hy), end=(dx+dw, dy), stroke="#000000", stroke_width=1))
    points.append((x+dataWidth, hy))
    dwgData.add(dwg.polyline(points=points, stroke="#000000", stroke_width=1.5, fill="none"))

    # draw slr data labels
    maxSlr = max([d["value"] for d in station["slrData"]])
    for l in SLR_LABELS:
        if l["value"] < maxSlr:
            py = mu.norm(l["value"], minSlrValue, maxSlrValue)
            dy = hy - py * dataHeight
            dx0 = x
            for d in station["slrData"]:
                if d["value"] >= l["value"]:
                    px = mu.norm(d["year"]+1, YEAR_START, YEAR_END+1)
                    dx0 = x + px * dataWidth
            dx1 = x + dataWidth + TICK_WIDTH
            dwgAxis.add(dwg.line(start=(dx0,dy), end=(dx1, dy), stroke="#000000", stroke_width=1, stroke_dasharray="3,1"))
            dwgLabels.add(dwg.text(l["label"], insert=(dx1+2, dy), alignment_baseline="middle", font_size=12))

    # draw inund data labels
    maxInund = max([d["value"] for d in station["inundationData"]])
    for l in INUNDATION_LABELS:
        if l["value"] < maxInund:
            py = mu.norm(l["value"], minInundValue, maxInundValue)
            dy = hy + py * dataHeight
            dx0 = x
            for d in station["inundationData"]:
                if d["value"] >= l["value"]:
                    px = mu.norm(d["year"]+1, YEAR_START, YEAR_END+1)
                    dx0 = x + px * dataWidth
            dx1 = x + dataWidth + TICK_WIDTH
            dwgAxis.add(dwg.line(start=(dx0,dy), end=(dx1, dy), stroke="#000000", stroke_width=1, stroke_dasharray="3,1"))
            dwgLabels.add(dwg.text(l["label"], insert=(dx1+2, dy), alignment_baseline="middle", font_size=12))

    # INCHES_PER_METER

    y += stationHeight + MARGIN

dwg.add(dwg.rect(insert=(PAD,PAD), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))

# Save svg
dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
