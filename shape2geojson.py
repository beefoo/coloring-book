# -*- coding: utf-8 -*-

# Usage
#   python shape2geojson.py -in tmp/data/shapfile -out tmp/output/out.json

import argparse
import json
import shapefile # https://github.com/GeospatialPython/pyshp

# input
parser = argparse.ArgumentParser()
parser.add_argument('-in', dest="INPUT_FILE", default="path/to/shapefile", help="Path to input shape files")
parser.add_argument('-out', dest="OUTPUT_FILE", default="path/to/geo.json", help="Path to output geojson file")

# init input
args = parser.parse_args()

# convert shapefile to geojson
sf = shapefile.Reader(args.INPUT_FILE)
fields = sf.fields[1:]
field_names = [field[0] for field in fields]
features = []
for sr in sf.shapeRecords():
    atr = dict(zip(field_names, sr.record))
    geom = sr.shape.__geo_interface__
    features.append({
        "type": "Feature",
        "geometry": geom,
        "properties": atr
    })
geojson = {"type": "FeatureCollection", "features": features}

with open(args.OUTPUT_FILE, 'w') as f:
    json.dump(geojson, f)
    print "Wrote geojson to file %s" % args.OUTPUT_FILE
