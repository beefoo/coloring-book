# -*- coding: utf-8 -*-

import argparse
import calendar
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

import lib.svgutils as svgu

# input
parser = argparse.ArgumentParser()
# input source: https://www.ncdc.noaa.gov/monitoring-references/faq/anomalies.php
parser.add_argument('-input', dest="INPUT_FILE", default="data/188001-201612_land_ocean.csv", help="Path to input file")
parser.add_argument('-ys', dest="YEAR_START", type=int, default=1880, help="Year start on viz")
parser.add_argument('-width', dest="WIDTH", type=int, default=800, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=int, default=1200, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=int, default=60, help="Padding of output file")

# init input
args = parser.parse_args()
WIDTH = args.WIDTH
HEIGHT = args.HEIGHT
YEAR_START = args.YEAR_START
PAD = args.PAD

values = []

# read csv
with open(args.INPUT_FILE, 'rb') as f:
    r = csv.reader(f, delimiter=',')
    for skip in range(4):
        next(r, None)
    # for each row
    for _year,_value in r:
        value = {
            "index": len(values),
            "key": _year,
            "year": int(_year[:4]),
            "month": int(_year[4:]) - 1,
            "value": float(_value)
        }
        values.append(value)

# init svg
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')

dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
