# -*- coding: utf-8 -*-

# Solar source
# NREL - Solar Summaries: Spreadsheet of annual 10-Kilometer solar data (DNI, LATTILT and GHI) data by state and zip code
# http://www.nrel.gov/gis/data_solar.html

# Wind source
# NREL - United States Wind Power Class - no exclusions - 50m
# http://www.nrel.gov/gis/data_wind.html
# http://www.nrel.gov/gis/wind_detail.html

import argparse
import csv
import inspect
import json
import math
import os
import svgwrite
import sys

# add parent directory to sys path to import relative modules
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import lib.geoutils as gu
import lib.mathutils as mu

# input
parser = argparse.ArgumentParser()
parser.add_argument('-geo', dest="GEO_FILE", default="data/USA.geo.json", help="Geojson input file")
parser.add_argument('-width', dest="WIDTH", type=float, default=11, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=float, default=8.5, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=float, default=0.5, help="Padding of output file")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/re_map_%s.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
DPI = 72
PAD = args.PAD * DPI
WIDTH = args.WIDTH * DPI - PAD * 2
HEIGHT = args.HEIGHT * DPI - PAD * 2

# config
CONFIG = {
    "solar": {
        "file": "data/lat_lng_ghi.csv"
    },
    "wind": {
        "file": "data/lat_lng_wind.csv"
    }
}
LABELS = {
    "solar": [
        {"display": "1", "value": 3.5, "description": "", "color": "#000000"},
        {"display": "2", "value": 4, "description": "", "color": "#333333"},
        {"display": "3", "value": 4.5, "description": "", "color": "#666666"},
        {"display": "4", "value": 5, "description": "", "color": "#999999"},
        {"display": "5", "value": 5.5, "description": "", "color": "#CCCCCC"},
        {"display": "6", "value": 6, "description": "", "color": "#FFFFFF"}
    ],
    "wind": [
        {"display": "1", "value": 1, "description": "", "color": "#FFFFFF"},
        {"display": "2", "value": 2, "description": "", "color": "#CCCCCC"},
        {"display": "3", "value": 3, "description": "", "color": "#999999"},
        {"display": "4", "value": 4, "description": "", "color": "#666666"},
        {"display": "5", "value": 5, "description": "", "color": "#333333"},
        {"display": "6", "value": 6, "description": "", "color": "#000000"}
    ]
}

def getLabel(labels, value):
    label = labels[-1]
    for l in labels:
        if value <= l["value"]:
            label = l
            break
    return label

def parseNumber(string):
    try:
        num = float(string)
        if "." not in string:
            num = int(string)
        return num
    except ValueError:
        return string

def parseNumbers(arr):
    for i, item in enumerate(arr):
        for key in item:
            arr[i][key] = parseNumber(item[key])
    return arr

def readCSV(filename):
    rows = []
    with open(filename, 'rb') as f:
        lines = [line for line in f if not line.startswith("#")]
        reader = csv.DictReader(lines, skipinitialspace=True)
        rows = list(reader)
        rows = parseNumbers(rows)
    return rows

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

def makeMap(name, coordinates):
    global CONFIG
    global LABELS

    filename = CONFIG[name]["file"]
    labels = LABELS[name]
    data = readCSV(filename)

    # only use data that's within coordinates
    data = [d for d in data if gu.withinCoordinates(coordinates, (d["lng"]+0.5, d["lat"]+0.5))]

    # Init svg
    outfilename = args.OUTPUT_FILE % name
    dwg = svgwrite.Drawing(outfilename, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
    dwgCells = dwg.add(dwg.g(id="cells"))
    dwgLabels = dwg.add(dwg.g(id="labels"))

    # get bounds, ratio
    bounds = gu.getBounds(coordinates)
    (rw, rh) = gu.getRatio(coordinates)

    # make calculations
    width = 1.0 * WIDTH
    height = width * rh / rw
    lngDiff = abs(bounds[2]-bounds[0])
    latDiff = abs(bounds[3]-bounds[1])
    cellW = width / (lngDiff+1)
    cellH = height / (latDiff+1)
    halfW = cellW * 0.5
    halfH = cellH * 0.5
    offsetX = PAD
    offsetY = PAD + (HEIGHT - height) * 0.667

    lnglats = []
    for d in data:
        (x, y) = gu.coordinateToPixel((d["lng"]+0.5, d["lat"]+0.5), width, height, bounds)
        label = getLabel(labels, d["value"])
        color = label["color"]
        # color = "none"
        x += offsetX
        y += offsetY
        points = [(x,y-halfW), (x+halfW,y), (x,y+halfW), (x-halfW,y), (x,y-halfW)]
        dwgCells.add(dwg.polygon(id="l%s_%s" % (d["lng"],d["lat"]), points=points, fill=color, stroke="#000000", stroke_width=1))
        lnglats.append("%s,%s" % (d["lng"],d["lat"]))

    dwg.add(dwg.rect(insert=(PAD,PAD), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))
    dwg.save()
    print "Saved svg: %s" % outfilename
    return lnglats

lnglats1 = makeMap("solar", coordinates)
lnglats2 = makeMap("wind", coordinates)

# lnglats = [l.split(",") for l in list(set(lnglats1 + lnglats2))]
# lnglats = sorted(lnglats, key=lambda lnglat: lnglat[1])
# lnglats = sorted(lnglats, key=lambda lnglat: lnglat[0])
# with open("data/us_lng_lats.csv", 'wb') as f:
#     w = csv.writer(f, delimiter=',')
#     w.writerow(['lng', 'lat'])
#     for lnglat in lnglats:
#         w.writerow(lnglat)
