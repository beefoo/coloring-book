# -*- coding: utf-8 -*-

# Usage:
#   python flux.py
#   python flux.py -geo data/CHN.geo.json -color True

# Data source:
# https://www.esrl.noaa.gov/gmd/ccgg/carbontracker/fluxes.php

import argparse
import base64
from collections import Counter
import csv
import inspect
import json
import math
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.cluster.vq import kmeans, vq
import svgwrite
import sys

# add parent directory to sys path to import relative modules
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import lib.geoutils as gu

# input
parser = argparse.ArgumentParser()
parser.add_argument('-in', dest="INPUT_FILE", default="data/CT2015_flux1x1_longterm.csv", help="Input data file")
parser.add_argument('-geo', dest="GEO_FILE", default="data/USA.geo.json", help="Input geojson file")
parser.add_argument('-width', dest="WIDTH", type=float, default=11, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=float, default=8.5, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=float, default=0.5, help="Padding of output file")
parser.add_argument('-color', dest="SHOW_COLOR", type=bool, default=False, help="Whether or not to display color")
parser.add_argument('-out', dest="OUTPUT_FILE", default="data/flux_%s.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
DPI = 72
PAD = args.PAD * DPI
WIDTH = args.WIDTH * DPI - PAD * 2
HEIGHT = args.HEIGHT * DPI - PAD * 2
SHOW_COLOR = args.SHOW_COLOR
Y_OFFSET = 0.1 * HEIGHT
LATS = 180
LONS = 360

GROUPS = [
    {"key": "1", "min": 0, "label": "Under 1 metric ton", "color": "#90b272", "image": "data/white.png"},
    {"key": "2", "min": 1, "label": "1 to 10 metric tons", "color": "#c6ce4e", "image": "data/yellow.png"},
    {"key": "3", "min": 10, "label": "10 to 100 metric tons", "color": "#ceab4e", "image": "data/orange.png"},
    {"key": "4", "min": 100, "label": "100 to 500 metric tons", "color": "#d86969", "image": "data/red.png"},
    {"key": "5", "min": 500, "label": "500 to 1000 metric tons", "color": "#a82222", "image": "data/brown.png"},
    {"key": "6", "min": 1000, "label": "Over 1000 metric tons", "color": "#7c139e", "image": "data/black.png"}
]

def getGroup(value, groups):
    group = None
    for g in groups:
        if value < g["min"]:
            break
        group = g
    return group

data = []
# read csv
with open(args.INPUT_FILE, 'rb') as f:
    r = csv.reader(f, delimiter=',')
    # skip header
    next(r, None)
    # put data in matrix
    i = 0
    for _lat, _lon, _value in r:
        v = float(_value)
        if v >= 0:
            data.append({
                "index": i,
                "lat": float(_lat),
                "lon": float(_lon),
                "row": LATS - (i / LONS) - 1,
                "col": i % LONS,
                "value": v
            })
        i += 1
print "%s valid data points found" % len(data)

# retrieve geo coordinates
geodata = {}
with open(args.GEO_FILE) as f:
    geodata = json.load(f)
coordinates = []
for feature in geodata["features"]:
    t = feature["geometry"]["type"]
    gcoordinates = feature["geometry"]["coordinates"]
    if t == "MultiPolygon":
        gcoordinates = sorted(gcoordinates, key=lambda c: -1*len(c[0]))
    else:
        gcoordinates = sorted(gcoordinates, key=lambda c: -1*len(c))
    for coordinate in gcoordinates:
        if t == "MultiPolygon":
            coordinates.append(coordinate[0])
        else:
            coordinates.append(coordinate)
        break # only show biggest shape

# only use data that's within coordinates
data = [d for d in data if gu.withinCoordinates(coordinates, (d["lon"], d["lat"]))]
print "%s data points found in %s" % (len(data), args.GEO_FILE)

# flatten coordinates
flattenedCoordinates = []
for coords in coordinates:
    for p in coords:
        flattenedCoordinates.append(p)

# get bounds, ratio
bounds = gu.getBounds(flattenedCoordinates)
print "Bounds: (%s, %s) (%s, %s)" % bounds
(rw, rh) = gu.getRatio(flattenedCoordinates)
print "Ratio: %s x %s" % (rw, rh)

# add groups
for i, d in enumerate(data):
    data[i]["group"] = getGroup(d["value"], GROUPS)

# give groups stats
groupValues = [d["group"]["key"] for d in data]
C = Counter(groupValues)
print "Group stats:"
for k,v in C.items():
    print "Group: %s, Size: %s" % (k, v)

# get the bounds
cols = [d["col"] for d in data]
minCols = min(cols)
maxCols = max(cols)
colDiff = maxCols - minCols
rows = [d["row"] for d in data]
minRows = min(rows)
maxRows = max(rows)
rowDiff = maxRows - minRows
# normalize row/col
for i, d in enumerate(data):
    data[i]["row"] = d["row"] - minRows
    data[i]["col"] = d["col"] - minCols

# calculate dimensions

width = 1.0 * WIDTH
height = width * rh / rw
cellW = width / (colDiff+1)
cellH = height / (rowDiff+1)
halfW = cellW * 0.5
halfH = cellH * 0.5
offsetX = PAD
offsetY = PAD + (HEIGHT - height) * 0.667

# init svg
prefix = args.GEO_FILE.split("/")[1].split(".")[0]
filename = args.OUTPUT_FILE % prefix
dwg = svgwrite.Drawing(filename, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')

# define color patterns
if SHOW_COLOR:
    for g in GROUPS:
        imageSize = (300, 300)
        imageData = ""
        with open(g["image"], "rb") as f:
            imageData = base64.b64encode(f.read())
        dwgImage = dwg.image(href="data:image/png;base64,%s" % imageData, insert=(0, 0), size=imageSize)
        dwgPattern = dwg.pattern(id="pattern%s" % g["key"], patternUnits="userSpaceOnUse", size=imageSize)
        dwgPattern.add(dwgImage)
        dwg.defs.add(dwgPattern)

# add cells and labels
cellsGroup = dwg.add(dwg.g(id="cells"))
labelsGroup = dwg.add(dwg.g(id="labels"))
labelsGroups = {}
for g in GROUPS:
    labelsGroups[g["key"]] = labelsGroup.add(dwg.g(id="labels%s" % g["key"]))
for d in data:
    # (x, y) = gu.coordinateToPixel((d["lon"], d["lat"]), width, height, bounds)
    x = d["col"] * cellW + offsetX
    y = d["row"] * cellH + offsetY
    color = "none"
    if SHOW_COLOR:
        # color = d["group"]["color"]
        color = "url(#pattern%s)" % d["group"]["key"]
    # cellsGroup.add(dwg.rect(insert=(x, y), size=(cellW, cellH), fill=color, stroke="#000000", stroke_width=1))
    cellsGroup.add(dwg.ellipse(center=(x+halfW, y+halfH), r=(halfW, halfH), fill=color, stroke="#000000", stroke_width=1))
    labelsGroups[d["group"]["key"]].add(dwg.text(d["group"]["key"], insert=(x+halfW, y+halfH), text_anchor="middle", alignment_baseline="middle", font_size=11))

dwg.add(dwg.rect(insert=(PAD,PAD), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))
dwg.save()
print "Saved svg: %s" % filename

# get clusters
# y = np.array(values)
# clusters, distortion = kmeans(y, 5)  # five clusters
# cluster_indices, dist = vq(y, clusters)
# C = Counter(cluster_indices.tolist())
# print "Clusters:"
# for k,v in C.items():
#     print "Cluster: %s, Size: %s" % (clusters[k], v)
