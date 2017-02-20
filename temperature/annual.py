# -*- coding: utf-8 -*-

import csv
import sys

# read csv
values = []
with open('data/1880-2016_land_ocean.csv', 'rb') as f:
    r = csv.reader(f, delimiter=',')
    header = next(r, None)
    # for each row
    for _year,_value in r:
        value = {
            "year": int(_year),
            "value": float(_value)
        }
        values.append(value)

values = sorted(values, key=lambda k: -k["value"])

print "Hottest years in order:"
for i, v in enumerate(values):
    print "%s. %s" % (i+1, v["year"])
    if i >= 19:
        break
