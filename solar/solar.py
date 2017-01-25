# -*- coding: utf-8 -*-

# Home energy use data source:
# https://www.epa.gov/energy/greenhouse-gases-equivalencies-calculator-calculations-and-references#houseenergy

# Solar panel data source:
# https://www.google.com/get/sunroof which uses:
    # https://www.census.gov/geo/maps-data/data/tiger-data.html
    # https://nsrdb.nrel.gov/
    # http://apps1.eere.energy.gov/sled/#/

# GeoJSON files
# http://www.zillow.com/howto/api/neighborhood-boundaries.htm
# http://catalog.opendata.city/lv/dataset/oklahoma-cities-polygon

# Shapefiles
# http://www.co.fresno.ca.us/DepartmentPage.aspx?id=52122
# https://data.sfgov.org/Government/Bay-Area-Cities-Zipped-Shapefile-Format-/nghj-u9xk/data

import argparse
import inspect
import math
import os
from pprint import pprint
# from shapely.geometry import Polygon
# from shapely.ops import cascaded_union
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
parser.add_argument('-height', dest="HEIGHT", type=int, default=1035, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=int, default=100, help="Padding of output file")
parser.add_argument('-report', dest="REPORT", type=bool, default=False, help="Output report")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/solar.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
WIDTH = args.WIDTH
HEIGHT = args.HEIGHT
PAD = args.PAD
REPORT = args.REPORT

# config display
CENTER_MARGIN = 20
CITY_HEIGHT = 0.5 * (HEIGHT - CENTER_MARGIN)

# On average, each home consumed 12,183 kWh of delivered electricity (EIA 2015a).
ENERGY_CONSUMED_PER_HOME = 12183

# Project Sunroof data
# https://www.google.com/get/sunroof
CITY_ROOFTOP_DATA = {
    "san_jose": {
        "label": "San Jose, CA",
        "households": 301366, # http://www.census.gov/2010census/popmap/ipmtext.php?fl=06:0668000
        "rooftops": 205000,
        "electricity": 5800000000, # kWh AC per yr
        "source": "https://www.google.com/get/sunroof/data-explorer/place/ChIJ9T_5iuTKj4ARe3GfygqMnbk/",
        "geojson": {
            "filename": "data/CA.geo.json",
            "key": "CITY",
            "value": "San Jose"
        }
    },
    "fresno": {
        "label": "Fresno, CA",
        "households": 158349, # http://www.census.gov/2010census/popmap/ipmtext.php?fl=06:0627000
        "rooftops": 148000,
        "electricity": 4800000000, # kWh AC per yr
        "source": "https://www.google.com/get/sunroof/data-explorer/featured/2/fresno",
        "geojson": {
            "filename": "data/CA.geo.json",
            "key": "CITY",
            "value": "Fresno"
        },
        "shapefile": "data/fresno_city/fresno_city"
    },
    "oklahoma_city": {
        "label": "Oklahoma City, OK",
        "households": 230233, # http://www.census.gov/2010census/popmap/ipmtext.php?fl=4055000
        "rooftops": 200000,
        "electricity": 5300000000, # kWh AC per yr
        "source": "https://www.google.com/get/sunroof/data-explorer/featured/1/oklahoma-city",
        "geojson": "data/oklahoma_cities.geojson"
    },
    "san_francisco": {
        "label": "San Francisco, CA",
        "households": 345811, # http://www.census.gov/2010census/popmap/ipmtext.php?fl=0667000
        "rooftops": 123000,
        "electricity": 2400000000, # kWh AC per yr
        "source": "https://www.google.com/get/sunroof/data-explorer/place/ChIJIQBpAG2ahYAR_6128GcTUEo/",
        "geojson": {
            "filename": "data/CA.geo.json",
            "key": "CITY",
            "value": "San Francisco"
        },
        "shapefile": "data/san_francisco/san_francisco"
    }
}

# Make calculations
data = CITY_ROOFTOP_DATA.copy()
for key, d in CITY_ROOFTOP_DATA.iteritems():
    data[key]["electricityPerHousehold"] = int(round(1.0 * d["electricity"] / d["rooftops"]))
    forHouseholds = int(round(1.0 * d["electricity"] / ENERGY_CONSUMED_PER_HOME))
    data[key]["surplusHousholds"] = int(forHouseholds - d["rooftops"])
    data[key]["percentSurplus"] = int(round(1.0 * forHouseholds / d["rooftops"] * 100))
    data[key]["citySurplusHouseholds"] = int(forHouseholds - d["households"])
    data[key]["cityPercentSurplus"] = int(round(1.0 * forHouseholds / d["households"] * 100))
    data[key]["forHouseholds"] = forHouseholds

# Print report
if REPORT:
    for key, d in data.iteritems():
        print "%s:" % d["label"]
        print " - %s rooftops" % "{:,}".format(d["rooftops"])
        print " - %s kWh/year/household" % "{:,}".format(d["electricityPerHousehold"])
        print " - enough electricity for %s households" % "{:,}".format(d["forHouseholds"])
        print " - %s (+%s%%) surplus households" % ("{:,}".format(d["surplusHousholds"]), d["percentSurplus"])
        print " - %s city households" % "{:,}".format(d["households"])
        if d["citySurplusHouseholds"] > 0:
            print " - %s (+%s%%) city surplus households" % ("{:,}".format(d["citySurplusHouseholds"]), d["cityPercentSurplus"])
        print "-----"

# Define what we want to display
source = data["fresno"]
destination = data["san_francisco"]

# Display how much energy is supplied for destination from source
percentSupplied = int(round(1.0 * source["forHouseholds"] / destination["households"] * 100))
print "%s creates energy for %s households" % (source["label"], "{:,}".format(source["forHouseholds"]))
print "%s has %s households (%s%% supplied w/ energy)" % (destination["label"], "{:,}".format(destination["households"]), percentSupplied)

# Init geojson
sourceGeo = geo.GeoJSONUtil(source["geojson"]["filename"], source["geojson"]["key"], source["geojson"]["value"])
destGeo = geo.GeoJSONUtil(destination["geojson"]["filename"], destination["geojson"]["key"], destination["geojson"]["value"])
# sourceGeo.onlyBiggestShape()
# destGeo.onlyBiggestShape()

# determine relative size
(sw, sh) = sourceGeo.getDimensions()
(dw, dh) = destGeo.getDimensions()
cityRatio = 1.0 * WIDTH / CITY_HEIGHT

print "Source: (%s, %s), Dest: (%s, %s)" % (sw, sh, dw, dh)

# determine source width
sourceRatio = dw / dh
sourceWidth = 1.0 * WIDTH
sourceHeight = CITY_HEIGHT
if sourceRatio < cityRatio:
    sourceWidth = CITY_HEIGHT * sourceRatio
else:
    sourceHeight = 1.0 * WIDTH / sourceRatio

# determine destination width and offset
destRatio = dw / dh
destWidth = 1.0 * WIDTH
destHeight = CITY_HEIGHT
if destRatio < cityRatio:
    destWidth = CITY_HEIGHT * destRatio
else:
    destHeight = 1.0 * WIDTH / destRatio

# determine offsets
sx = PAD
sy = PAD
dx = PAD
dy = PAD + CITY_HEIGHT + CENTER_MARGIN

if sourceWidth < WIDTH:
    sx += (WIDTH - sourceWidth) * 0.5
if sourceHeight < CITY_HEIGHT:
    sy += (CITY_HEIGHT - sourceHeight) * 0.5
if destWidth < WIDTH:
    dx += (WIDTH - destWidth) * 0.5
if destHeight < CITY_HEIGHT:
    dy += (CITY_HEIGHT - destHeight) * 0.5

# retrieve polygons
sourcePolygons = sourceGeo.toPolygons(sourceWidth, sx, sy)
destPolygons = destGeo.toPolygons(destWidth, dx, dy)

# retrieve polygons
sourcePolygons = sourceGeo.toPolygons(sourceWidth, sx, sy)
destPolygons = destGeo.toPolygons(destWidth, dx, dy)

# sourcePolygon = cascaded_union([Polygon(p) for p in sourcePolygons])
# destPolygon = cascaded_union([Polygon(p) for p in destPolygons])

# init svg
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')

# draw polygons
# dwgGeo = dwg.g(id="geo")
# polygons = [sourcePolygon, destPolygon]
# for polygon in polygons:
#     dwgGeo.add(dwg.polygon(points=polygon.exterior.coords, stroke_width=2, stroke="#000000", fill="none"))
# dwg.add(dwgGeo)

# draw polygons
polygons = [sourcePolygons, destPolygons]
for i, polys in enumerate(polygons):
    dwgG = dwg.g(id="geo%s" % i)
    for poly in polys:
        dwgG.add(dwg.polygon(points=poly, stroke_width=2, stroke="#000000", fill="none"))
    dwg.add(dwgG)

dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
