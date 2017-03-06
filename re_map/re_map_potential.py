# -*- coding: utf-8 -*-

# Data from U.S. Renewable Energy Technical Potentials: A GIS-Based Analysis
# Lopez, A. et al. (2012). "U.S. Renewable Energy Technical Potentials: A GIS-Based Analysis." NREL/TP-6A20-51946. Golden, CO: National Renewable Energy Laboratory.
# http://www.nrel.gov/gis/re_potential.html

# Geojson from
# http://eric.clst.org/Stuff/USGeoJSON
# https://carto.com/dataset/ne_50m_admin_1_states

import argparse
import csv
import inspect
import math
import os
import svgwrite
import sys

# add parent directory to sys path to import relative modules
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import lib.geojson as geo
import lib.mathutils as mu

# input
parser = argparse.ArgumentParser()
parser.add_argument('-input', dest="INPUT_FILE", default="data/renewable_energy_technical_potential_data.csv", help="Input file")
parser.add_argument('-geo', dest="GEO_FILE", default="data/ne_50m_admin_1_states.geojson", help="Geojson input file")
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
GEOJSON_KEY = "name"
KEYS = {
    "solar": ["Urban Utility-scale PV (GWh)", "Rural Utility-scale PV (GWh)", "Rooftop PV (GWh)", "CSP (GWh)"],
    "wind": ["Onshore Wind (GWh)", "Offshore Wind (GWh)"]
}
LABELS = {
    "solar": [
        {"display": "", "value": 0, "description": "none"},
        {"display": "1", "value": 1000, "description": "<= 1,000 TWh"},
        {"display": "2", "value": 5000, "description": "1,000 - 5,000 TWh"},
        {"display": "3", "value": 10000, "description": "5,000 - 10,000 TWh"},
        {"display": "4", "value": 20000, "description": "10,000 - 20,000 TWh"},
        {"display": "5", "value": 30000, "description": "20,000 - 30,000 TWh"},
        {"display": "6", "value": 50000, "description": "30,000+ TWh"}
    ],
    "wind": [
        {"display": "", "value": 0, "description": "none"},
        {"display": "1", "value": 500, "description": "<= 500 TWh"},
        {"display": "2", "value": 1000, "description": "500 - 1,000 TWh"},
        {"display": "3", "value": 2000, "description": "1,000 - 2,000 TWh"},
        {"display": "4", "value": 3000, "description": "2,000 - 3,000 TWh"},
        {"display": "5", "value": 4000, "description": "4,000 - 5,000 TWh"},
        {"display": "6", "value": 5000, "description": "4,000+ TWh"}
    ]
}

def parseNumber(string):
    try:
        string = string.replace(",","")
        if string == "NA":
            num = 0
        else:
            num = float(string)
        return num
    except ValueError:
        return string

def parseNumbers(arr):
    for i, item in enumerate(arr):
        for key in item:
            arr[i][key] = parseNumber(item[key])
    return arr

# read data
states = []
with open(args.INPUT_FILE, 'rb') as f:
    reader = csv.DictReader(f, skipinitialspace=True)
    rows = list(reader)
    states = parseNumbers(rows)

# read geojson for contiguous states
statesGeo = geo.GeoJSONUtil(args.GEO_FILE)
statesGeo.rejectFeatures(GEOJSON_KEY, "Alaska")
statesGeo.rejectFeatures(GEOJSON_KEY, "Hawaii")
statesGeo.rejectFeatures(GEOJSON_KEY, "District of Columbia")
(w,h) = statesGeo.getDimensions()
statesHeight = 1.0 * WIDTH * h / w
padY = PAD + HEIGHT - statesHeight
statePolys = statesGeo.toPolygons(WIDTH, PAD, padY)
stateNames = statesGeo.getProperties(GEOJSON_KEY)
statePolyDict = dict(zip(stateNames, statePolys))

# # read geojson for Alaska
# alaskaGeo = geo.GeoJSONUtil(args.GEO_FILE, GEOJSON_KEY, "Alaska")
# alaskaGeo.onlyBiggestShape()
# (w,h) = alaskaGeo.getDimensions()
# alaskaWidth = WIDTH * 0.2
# alaskaHeight = 1.0 * alaskaWidth * h / w
# padY = PAD + HEIGHT - statesHeight - alaskaHeight
# alaskaPolys = alaskaGeo.toPolygons(alaskaWidth, PAD, padY)
# statePolyDict["Alaska"] = alaskaPolys[0]
#
# # read geojson for Hawaii
# hawaiiGeo = geo.GeoJSONUtil(args.GEO_FILE, GEOJSON_KEY, "Hawaii")
# (w,h) = hawaiiGeo.getDimensions()
# hawaiiWidth = WIDTH * 0.6
# hawaiiHeight = 1.0 * hawaiiWidth * h / w
# padY = PAD + HEIGHT - statesHeight - hawaiiHeight
# hawaiiPolys = hawaiiGeo.toPolygons(hawaiiWidth, PAD+alaskaWidth, padY)
# statePolyDict["Hawaii"] = hawaiiPolys[0]

def makeMap(name, data, polys):
    global KEYS
    global LABELS
    filename = args.OUTPUT_FILE % name
    keys = KEYS[name]
    labels = LABELS[name]

    # init svg
    dwg = svgwrite.Drawing(filename, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
    dwgStates = dwg.add(dwg.g(id="states"))
    dwgLabels = dwg.add(dwg.g(id="labels"))

    for d in data:
        s = d["State"]
        # get value
        value = 0
        for k in keys:
            value += d[k]
        # convert GWh to TWh
        value = value / 1000.0
        # get label
        label = labels[-1]
        for l in labels:
            if value <= l["value"]:
                label = l
                break
        if s in polys:
            featurePolys = polys[s]
            centroid = mu.polygonCentroid(featurePolys[0])
            for points in featurePolys:
                # factor = 4
                # points = mu.simplify(points, max(len(points) / factor, 12))
                # points.append((points[0][0], points[0][1]))
                dwgStates.add(dwg.polygon(points=points, stroke_width=1, stroke_linejoin="round", stroke="#000000", fill="#ffffff"))
                if s != "Hawaii":
                    break
            if len(label["display"]):
                dwgLabels.add(dwg.text(label["display"], insert=centroid, text_anchor="middle", alignment_baseline="middle", font_size=12))
        else:
            print "Warning: %s not found in polys" % s

    dwg.add(dwg.rect(insert=(PAD,PAD), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))
    dwg.save()

makeMap("solar", states, statePolyDict)
makeMap("wind", states, statePolyDict)
