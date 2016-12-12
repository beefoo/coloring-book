# -*- coding: utf-8 -*-

import argparse
import json
import shapefile # https://github.com/GeospatialPython/pyshp
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-in', dest="INPUT_FILE", default="data/extent_N_%s_polyline_v2/extent_N_%s_polyline_v2", help="Path to input shapefiles")
parser.add_argument('-months', dest="MONTHS", default="199609,200609,201609", help="Months as a list")

# init input
args = parser.parse_args()

# convert shapefile to geojson
sfname = args.INPUT_FILE % ("197909", "197909")
sf = shapefile.Reader(sfname)
fields = reader.fields[1:]
field_names = [field[0] for field in fields]
buf = []
for sr in reader.shapeRecords():
   atr = dict(zip(field_names, sr.record))
   geom = sr.shape.__geo_interface__
   buf.append(dict(type="Feature", geometry=geom, properties=atr))
geojson = {"type": "FeatureCollection", "features": buf}
