# -*- coding: utf-8 -*-

# Usage:
#   python flux.py
#   python flux.py -geo data/CHN.geo.json -color True

import argparse
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

import lib.mathutils as mu

# input
parser = argparse.ArgumentParser()
parser.add_argument('-in', dest="INPUT_FILE", default="data/CT2015_flux1x1_longterm.csv", help="Input data file")
parser.add_argument('-geo', dest="GEO_FILE", default="data/USA.geo.json", help="Input geojson file")
parser.add_argument('-width', dest="WIDTH", type=int, default=1600, help="Width of output file")
parser.add_argument('-pad', dest="PAD", type=int, default=40, help="Padding of output file")
parser.add_argument('-color', dest="SHOW_COLOR", type=bool, default=False, help="Whether or not to display color")
parser.add_argument('-out', dest="OUTPUT_FILE", default="data/flux_%s.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
WIDTH = args.WIDTH
PAD = args.PAD
SHOW_COLOR = args.SHOW_COLOR

LATS = 180
LONS = 360

GROUPS = [
    {"key": "1", "min": 0, "label": "Under 1 metric ton", "color": "#90b272"},
    {"key": "2", "min": 1, "label": "1 to 10 metric tons", "color": "#c6ce4e"},
    {"key": "3", "min": 10, "label": "10 to 100 metric tons", "color": "#ceab4e"},
    {"key": "4", "min": 100, "label": "100 to 500 metric tons", "color": "#d86969"},
    {"key": "5", "min": 500, "label": "500 to 1000 metric tons", "color": "#a82222"},
    {"key": "6", "min": 1000, "label": "Over 1000 metric tons", "color": "#7c139e"}
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
        y = i / LONS
        x = i % LONS
        if v >= 0:
            data.append({
                "index": i,
                "x": x,
                "y": y,
                "lat": float(_lat),
                "lon": float(_lon),
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
    for coordinate in feature["geometry"]["coordinates"]:
        if t == "MultiPolygon":
            coordinates.append(coordinate[0])
        else:
            coordinates.append(coordinate)

def withinCoordinates(coords, p):
    within = False
    for c in coords:
        if mu.containsPoint(c, p):
            within = True
            break
    return within

# only use data that's within coordinates
data = [d for d in data if withinCoordinates(coordinates, (d["lon"], d["lat"]))]
print "%s data points found in %s" % (len(data), args.GEO_FILE)

# add groups, invert y
for i, d in enumerate(data):
    data[i]["group"] = getGroup(d["value"], GROUPS)
    data[i]["y"] = LATS - d["y"] - 1

# give groups stats
groupValues = [d["group"]["key"] for d in data]
C = Counter(groupValues)
print "Group stats:"
for k,v in C.items():
    print "Group: %s, Size: %s" % (k, v)

# get the bounds
xs = [d["x"] for d in data]
ys = [d["y"] for d in data]
minX = min(xs)
maxX = max(xs)
minY = min(ys)
maxY = max(ys)
print "Bounds: (%s, %s) (%s, %s)" % (minX, minY, maxX, maxY)

# calculate dimensions
xDiff = maxX - minX
yDiff = maxY - minY
cellW = 1.0 * WIDTH / xDiff
cellH = cellW
halfW = cellW * 0.5
halfH = cellH * 0.5
height = cellH * yDiff

# init svg
prefix = args.GEO_FILE.split("/")[1].split(".")[0]
filename = args.OUTPUT_FILE % prefix
dwg = svgwrite.Drawing(filename, size=(WIDTH+PAD*2, height+PAD*2), profile='full')

# add cells and labels
cellsGroup = dwg.add(dwg.g(id="cells"))
labelsGroup = dwg.add(dwg.g(id="labels"))
for d in data:
    x = (d["x"]-minX) * cellW + PAD
    y = (d["y"]-minY) * cellH + PAD
    color = "none"
    if SHOW_COLOR:
        color = d["group"]["color"]
    cellsGroup.add(dwg.rect(insert=(x, y), size=(cellW, cellH), fill=color, stroke="#000000", stroke_width=1))
    labelsGroup.add(dwg.text(d["group"]["key"], insert=(x+halfW, y+halfH), text_anchor="middle", alignment_baseline="middle", font_size=12))
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