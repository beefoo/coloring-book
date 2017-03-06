# -*- coding: utf-8 -*-

import csv
from collections import defaultdict
from pprint import pprint
import shapefile # https://github.com/GeospatialPython/pyshp
import sys

# NREL - United States Wind Power Class - no exclusions - 50m
# http://www.nrel.gov/gis/data_wind.html
# http://www.nrel.gov/gis/wind_detail.html

INPUT_FILE = 'ref_wind_no_excl/ref_wind_no_excl'
OUTPUT_FILE = 'data/lat_lng_wind.csv'

# Mean of list
def mean(data):
    n = len(data)
    if n < 1:
        return 0
    else:
        return 1.0 * sum(data) / n

def geometryLngLat(geometry):
    t = geometry["type"]
    gcoordinates = geometry["coordinates"]
    lngs = []
    lats = []
    for coordinates in gcoordinates:
        lnglats = coordinates
        if t == "MultiPolygon":
            lnglats = coordinates[0]
        for lnglat in lnglats:
            lngs.append(lnglat[0])
            lats.append(lnglat[1])
    return ((mean(lngs)), mean(lats))

# convert shapefile to geojson
print "Reading shapfile..."
sf = shapefile.Reader(INPUT_FILE)
fields = sf.fields[1:]
field_names = [field[0] for field in fields]

recordCount = len(sf.shapeRecords())
print "Found %s records" % recordCount
# pprint(field_names)

print "Processing records..."
data = {}
for i, sr in enumerate(sf.shapeRecords()):
    atr = dict(zip(field_names, sr.record))
    geom = sr.shape.__geo_interface__
    lnglat = geometryLngLat(geom)

    # group lat lngs
    key = "%s,%s" % (int(lnglat[0]), int(lnglat[1]))
    value = int(atr['wind_class'])
    if key in data:
        data[key].append(value)
    else:
        data[key] = [value]

    sys.stdout.write('\r')
    sys.stdout.write(str(round(1.0*i/recordCount*100,1))+'%')
    sys.stdout.flush()

print "\rGrouping records by lat/lon..."
rows = []
for key in data:
    entries = data[key]
    lnglat = [int(l) for l in key.split(",")]
    value = int(round(mean(entries)))
    rows.append([lnglat[0], lnglat[1], value])

print "Writing to file..."
with open(OUTPUT_FILE, 'wb') as f:
    w = csv.writer(f, delimiter=',')
    w.writerow(['lng', 'lat', 'value'])
    for row in rows:
        w.writerow(row)

print "Wrote %s rows to %s" % (len(rows), OUTPUT_FILE)
