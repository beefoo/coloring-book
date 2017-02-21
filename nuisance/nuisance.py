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
parser.add_argument('-y0', dest="YEAR_START", type=int, default=1981, help="Year start")
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
X_LABEL_HEIGHT = 0.2 * DPI
MARGIN = 0.333 * DPI
TICK_WIDTH = 0.1 * DPI

SLR_LABELS = [
    {"value": 0.127, "label": "5''"},
    {"value": 0.254, "label": "10''"}
]
INUNDATION_LABELS = [
    {"value": 5, "label": "5 or less", "key": "W", "color": "white"},
    {"value": 10, "label": "6 to 10", "key": "Y", "color": "yellow"},
    {"value": 20, "label": "11 to 20", "key": "O", "color": "orange"},
    {"value": 40, "label": "21 to 40", "key": "R", "color": "red"},
    {"value": 60, "label": "41 to 60", "key": "M", "color": "maroon"},
    {"value": 100, "label": "Over 60", "key": "B", "color": "brown"}
]

stationData = {}
with open(args.INPUT_FILE) as f:
    d = json.load(f)
    for stationId in STATIONS:
        sd = d["stationData"][stationId]
        # update station data to only valid year range
        slrd = [v for v in sd["slrData"] if v["year"] >= YEAR_START and v["year"] <= YEAR_END]
        inund = [v for v in sd["inundationData"] if v["year"] >= YEAR_START and v["year"] <= YEAR_END]
        # update ranges
        vs = [v["value"] for v in slrd]
        sd["slrRange"] = (min(vs), max(vs))
        vs = [v["value"] for v in inund]
        sd["inundationRange"] = (min(vs), max(vs))
        sd["slrData"] = slrd
        sd["inundationData"] = inund
        # add to station dictionary
        stationData[stationId] = sd

# Calculations
offsetY = PAD
offsetX = PAD
width = WIDTH+PAD*2
height = HEIGHT+PAD*2
stationHeight = 1.0 * (HEIGHT-MARGIN*(len(STATIONS)-1)) / len(STATIONS)
dataWidth = WIDTH - LABEL_WIDTH
dataHeight = stationHeight * 0.8
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
    y0 = y + dataHeight + (stationHeight - (dataHeight + X_LABEL_HEIGHT)) * 0.5
    x = offsetX

    # draw labels
    labelPad = 3
    labelX = x+LABEL_WIDTH_LEFT-labelPad
    labelY = y0
    if i <= 0:
        dwgLabels.add(dwg.text(str(YEAR_START-1), insert=(labelX, labelY), text_anchor="end", alignment_baseline="middle", font_size=12))
    labelX = x+LABEL_WIDTH_LEFT+dataWidth+labelPad
    if i <= 0:
        dwgLabels.add(dwg.text(str(YEAR_END), insert=(labelX, labelY), text_anchor="start", alignment_baseline="middle", font_size=12))
    x += LABEL_WIDTH_LEFT

    if i <= 0:
        labelX = x + dataWidth + LABEL_WIDTH_RIGHT
        labelY = y0 - dataHeight * 0.5
        dwgLabels.add(dwg.text("Mean sea level rise", insert=(labelX, labelY), text_anchor="middle", alignment_baseline="before-edge", font_size=12, dominant_baseline="central", transform="rotate(90,%s,%s)" % (labelX, labelY)))

    # draw station
    labelX = x
    labelY = y0 - dataHeight + MARGIN
    dwgLabels.add(dwg.text(station["label"], insert=(labelX, labelY), alignment_baseline="before-edge", font_size=16))

    # draw axis
    dwgAxis.add(dwg.line(start=(x, y0), end=(x+dataWidth, y0), stroke="#000000", stroke_width=1))

    # draw inundation data
    dw = dataWidth / yearCount
    colors = []
    for d in station["inundationData"]:
        px = mu.norm(d["year"], YEAR_START, YEAR_END+1)
        py = max(mu.norm(d["value"], minInundValue, maxInundValue), 0)
        dx = x + px * dataWidth + dw * 0.5
        dy = y0 + X_LABEL_HEIGHT
        label = INUNDATION_LABELS[-1]
        for l in INUNDATION_LABELS:
            if d["value"] <= l["value"]:
                label = l
                break
        dwgLabels.add(dwg.text(label["key"], insert=(dx, dy), text_anchor="middle", font_size=12))
        colors.append(label["color"])

    # draw slr data
    points = [(x, y0)]
    for j,d in enumerate(station["slrData"]):
        px = mu.norm(d["year"], YEAR_START, YEAR_END+1)
        py = max(mu.norm(d["value"], minSlrValue, maxSlrValue), 0.02)
        dx = x + px * dataWidth
        dy = y0 - py * dataHeight
        points.append((dx, dy))
        points.append((dx+dw, dy))
        dwgData.add(dwg.line(start=(dx+dw, y0), end=(dx+dw, dy), stroke="#000000", stroke_width=1))
        # dwgData.add(dwg.rect(insert=(dx, dy), size=(dw, py * dataHeight), fill=colors[j]))
    points.append((x+dataWidth, y0))
    dwgData.add(dwg.polyline(points=points, stroke="#000000", stroke_width=1.5, fill="none"))

    # draw slr data labels
    maxSlr = max([d["value"] for d in station["slrData"]])
    for l in SLR_LABELS:
        if l["value"] < maxSlr:
            py = mu.norm(l["value"], minSlrValue, maxSlrValue)
            dy = y0 - py * dataHeight
            dx0 = x
            for d in station["slrData"]:
                if d["value"] >= l["value"]:
                    px = mu.norm(d["year"]+1, YEAR_START, YEAR_END+1)
                    dx0 = x + px * dataWidth
            dx1 = x + dataWidth + TICK_WIDTH
            dwgAxis.add(dwg.line(start=(dx0,dy), end=(dx1, dy), stroke="#000000", stroke_width=1, stroke_dasharray="3,1"))
            dwgLabels.add(dwg.text(l["label"], insert=(dx1+2, dy), alignment_baseline="middle", font_size=12))

    y += stationHeight + MARGIN

dwg.add(dwg.rect(insert=(PAD,PAD), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))

# Save svg
dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
