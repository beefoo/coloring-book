# -*- coding: utf-8 -*-

# GeoJSON files
# http://www.zillow.com/howto/api/neighborhood-boundaries.htm
# http://catalog.opendata.city/lv/dataset/oklahoma-cities-polygon
# https://github.com/codeforamerica/click_that_hood/tree/master/public/data

# Shapefiles
# http://www.co.fresno.ca.us/DepartmentPage.aspx?id=52122
# https://data.sfgov.org/Government/Bay-Area-Cities-Zipped-Shapefile-Format-/nghj-u9xk/data

import argparse
import inspect
import math
import os
from pprint import pprint
from shapely.geometry import Polygon
from shapely.ops import cascaded_union
import svgwrite
import sys

# add parent directory to sys path to import relative modules
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import lib.geojson as geo

# input
parser = argparse.ArgumentParser()
parser.add_argument('-width', dest="WIDTH", type=int, default=800, help="Width of output file")
parser.add_argument('-pad', dest="PAD", type=int, default=100, help="Padding of output file")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/city_%s.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
WIDTH = args.WIDTH
PAD = args.PAD

# Init geojson
sourceGeo = geo.GeoJSONUtil("data/CA.geo.json", "CITY", "Fresno")
destGeo = geo.GeoJSONUtil("data/san-francisco.geojson")
destGeo.rejectFeatures("name", "Treasure Island/YBI")

geos = [
    # http://www.zillow.com/howto/api/neighborhood-boundaries.htm
    {"name": "fresno", "geo": sourceGeo},
    # https://github.com/codeforamerica/click_that_hood/blob/master/public/data/san-francisco.geojson
    {"name": "san_francisco", "geo": destGeo}
]

for g in geos:
    geo = g["geo"]
    filename = args.OUTPUT_FILE % g["name"]

    # determine height
    (w, h) = geo.getDimensions()
    height = WIDTH * (1.0 * h / w)

    # union polygons
    polygons = geo.toPolygons(WIDTH, PAD, PAD)
    unionedPoly = cascaded_union([Polygon(p) for p in polygons])

    # init svg
    dwg = svgwrite.Drawing(filename, size=(WIDTH+PAD*2, height+PAD*2), profile='full')

    # draw polygon
    if isinstance(unionedPoly, Polygon):
        dwg.add(dwg.polygon(points=unionedPoly.exterior.coords, stroke_width=1, stroke="#000000", fill="none"))

    # assume multi poly
    else:
        for poly in unionedPoly:
            dwg.add(dwg.polygon(points=poly.exterior.coords, stroke_width=1, stroke="#000000", fill="none"))

    dwg.save()
    print "Saved svg: %s" % filename
