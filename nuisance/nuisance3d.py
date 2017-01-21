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
parser.add_argument('-width', dest="WIDTH", type=int, default=1000, help="Width")
parser.add_argument('-height', dest="HEIGHT", type=int, default=647, help="Height")
parser.add_argument('-pad', dest="PAD", type=int, default=200, help="Year start")
parser.add_argument('-stations', dest="STATIONS", default="8575512,8665530,8658120", help="List of stations")
parser.add_argument('-y0', dest="YEAR_START", type=int, default=1951, help="Year start")
parser.add_argument('-y1', dest="YEAR_END", type=int, default=2015, help="Year end")
parser.add_argument('-out', dest="OUTPUT_FILE", default="data/nuisance_%s.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
WIDTH = args.WIDTH
HEIGHT = args.HEIGHT
PAD = args.PAD
STATIONS = args.STATIONS.split(",")
YEAR_START = args.YEAR_START
YEAR_END = args.YEAR_END
YEAR_COUNT = YEAR_END - YEAR_START + 1
STATION_COUNT = len(STATIONS)

# config bounds
X_OFFSET = 0.2
Y_OFFSET = 0.1
Z_MARGIN = 0.25
BOUNDS = {
    "tl": (0.0 * WIDTH + PAD, 0.5 * HEIGHT + PAD),
    "tr": ((0.5+X_OFFSET) * WIDTH + PAD, (0.0+Y_OFFSET) * HEIGHT + PAD),
    "bl": ((0.5-X_OFFSET) * WIDTH + PAD, (1.0-Y_OFFSET) * HEIGHT + PAD),
    "br": (1.0 * WIDTH + PAD, 0.5 * HEIGHT + PAD),
    "h": 0.35 * HEIGHT
}

# config labels
LABELS = {}
LABELS["years"] = [
    {"stationId": "8658120", "value": 1951, "label": "1950"},
    {"stationId": "8658120", "value": 2015, "label": "2015"}
]
LABELS["slrData"] = [
    {"stationId": "8658120", "value": 0.127, "label": "5'' rise"},
    {"stationId": "8658120", "value": 0.254, "label": "10'' rise"}
]
LABELS["inundationData"] = [
    {"stationId": "8658120", "value": 40, "label": "40 days"},
    {"stationId": "8658120", "value": 80, "label": "80 days"}
]

# load data
data = {}
stationData = {}
with open(args.INPUT_FILE) as f:
    data = json.load(f)
for stationId in STATIONS:
    stationData[stationId] = data["stationData"][stationId]

# Find data ranges
slrRange = [min([d["slrRange"][0] for k, d in stationData.iteritems()]), max([d["slrRange"][1] for k, d in stationData.iteritems()])]
inundationRange = [min([d["inundationRange"][0] for k, d in stationData.iteritems()]), max([d["inundationRange"][1] for k, d in stationData.iteritems()])]

def polylinesForBox(x0, y0, d1, d2, h):
    polylines = []

    # (x0, y0) is the bottom-left-back point of the box
    blb = (x0, y0)
    blf = (x0+d1[0], y0+d1[1])
    tlb = (x0, y0-h) #
    tlf = (x0+d1[0], y0+d1[1]-h) #
    trb = (x0+d2[0], y0-h-d2[1])
    trf = (x0+d1[0]+d2[0], y0+d1[1]-h-d2[1])
    brf = (x0+d1[0]+d2[0], y0+d1[1]-d2[1])

    # 3 polylines make up box
    polylineTop = [tlf, tlb, trb, trf]
    polylineLeft = [tlb, blb, blf, tlf]
    polylineRight = [tlf, trf, brf, blf]

    return [polylineTop, polylineLeft, polylineRight]

def makeSVG(dataKey, dataRange, filename):
    global stationData
    global LABELS

    # Init svg
    width = WIDTH+PAD*2
    height = HEIGHT+PAD*2
    dwg = svgwrite.Drawing(filename, size=(width, height), profile='full')
    dwgLabels = dwg.g(id="labels")
    dwgTicks = dwg.g(id="ticks")
    dwgData = dwg.g(id="data")
    pw = 1.0 / YEAR_COUNT
    pz = (1.0 - (Z_MARGIN * (STATION_COUNT-1))) / STATION_COUNT
    (x0, y0) = BOUNDS["tl"]
    (x1, y1) = BOUNDS["tr"]

    # how much to move per station
    (dx, dy) = mu.lerp2D(BOUNDS["tl"], BOUNDS["bl"], pz+Z_MARGIN)
    dx = abs(dx - x0)
    dy = abs(dy - y0)

    # how much to move per depth of box (z direction)
    (dx1, dy1) = mu.lerp2D(BOUNDS["tl"], BOUNDS["bl"], pz)
    d1 = (abs(dx1 - x0), abs(dy1 - y0))

    # how much to move per year (x direction)
    (dx2, dy2) = mu.lerp2D(BOUNDS["tl"], BOUNDS["tr"], pw)
    d2 = (abs(dx2 - x0), abs(dy2 - y0))

    for i, stationId in enumerate(STATIONS):
        station = stationData[stationId]
        # draw the data
        d = station[dataKey]
        # reverse the list
        d = sorted(d, key=lambda k: -k['year'])
        sdx = i * dx
        sdy = i * dy
        for item in d:
            if item["value"] < 0:
                continue
            px = mu.norm(item["year"], YEAR_START, YEAR_END)
            py = mu.norm(item["value"], dataRange[0], dataRange[1])
            (x, y) = mu.lerp2D((x0, y0), (x1, y1), px)
            x += sdx
            y += sdy
            h = BOUNDS["h"] * py
            # dwgData.add(dwg.circle(center=(x,y), r=2))
            # dwgData.add(dwg.line(start=(x, y), end=(x, y-h), stroke="#000000", stroke_width=1))
            polylines = polylinesForBox(x, y, d1, d2, h)
            for line in polylines:
                dwgData.add(dwg.polyline(points=line, stroke="#000000", stroke_width=1, fill="#FFFFFF"))

        # draw station labels
        (x, y) = BOUNDS["tl"]
        x += sdx
        y += sdy + d1[1] * 0.667
        dwgLabels.add(dwg.text(station["label"], insert=(x, y), text_anchor="end", alignment_baseline="middle", font_size=16))

        # draw year labels
        for label in LABELS["years"]:
            if label["stationId"] != stationId:
                continue
            px = mu.norm(label["value"], YEAR_START, YEAR_END)
            (x, y) = mu.lerp2D((x0, y0), (x1, y1), px)
            x += sdx + d1[0]
            y += sdy + d1[1]
            if px >= 1:
                x += d2[0]
                y -= d2[1]
            x2 = x + dx*0.1
            y2 = y + dy*0.1
            dwgTicks.add(dwg.line(start=(x, y), end=(x2, y2), stroke="#000000", stroke_width=1))
            dwgLabels.add(dwg.text(label["label"], insert=(x2+5, y2), alignment_baseline="before-edge", font_size=16))

        # draw data labels
        for label in LABELS[dataKey]:
            if label["stationId"] != stationId:
                continue
            py = mu.norm(label["value"], dataRange[0], dataRange[1])
            h = BOUNDS["h"] * py
            (x, y) = mu.lerp2D((x0, y0), (x1, y1), 1.0)
            x += sdx + d1[0] + d2[0]
            y += sdy + d1[1] - d2[1] - h
            x2 = x+dx*0.1
            y2 = y
            dwgTicks.add(dwg.line(start=(x, y), end=(x2, y2), stroke="#000000", stroke_width=1))
            dwgLabels.add(dwg.text(label["label"], insert=(x2+5, y2), alignment_baseline="middle", font_size=16))

    # dwgData.add(dwg.line(start=(x0, y0), end=(x0 + d1[0], y0 + d1[1]), stroke="#000000", stroke_width=1))
    # dwgData.add(dwg.line(start=(x0, y0), end=(x0 + d2[0], y0 - d2[1]), stroke="#000000", stroke_width=1))

    # Save svg
    dwg.add(dwgData)
    dwg.add(dwgTicks)
    dwg.add(dwgLabels)
    dwg.save()
    print "Saved svg: %s" % filename

makeSVG("slrData", slrRange, args.OUTPUT_FILE % "slr")
makeSVG("inundationData", inundationRange, args.OUTPUT_FILE % "inundation")
