# -*- coding: utf-8 -*-

import csv
import sys

# NREL - Solar Summaries: Spreadsheet of annual 10-Kilometer solar data (DNI, LATTILT and GHI) data by state and zip code
# http://www.nrel.gov/gis/data_solar.html

INPUT_FILE = 'data/solar_summaries_ghi_zip_code.csv'
ZIPCODE_FILE = 'data/zipcodes_latlng.csv'
OUTPUT_FILE = 'data/lat_lng_ghi.csv'
EXCLUDE = ['HI', 'AK']

# Mean of list
def mean(data):
    n = len(data)
    if n < 1:
        return 0
    else:
        return 1.0 * sum(data) / n

def parseNumber(string):
    try:
        num = float(string)
        return num
    except ValueError:
        return 0

zipcodes = {}
with open(ZIPCODE_FILE, 'rb') as f:
    r = csv.reader(f, delimiter=',')
    header = next(r, None)
    for zipcode, lat, lng in r:
        zipcodes[zipcode] = (int(float(lng)), int(float(lat)))

data = {}
with open(INPUT_FILE, 'rb') as f:
    r = csv.reader(f, delimiter=',')
    header = next(r, None)
    for line in r:
        zipcode = str(int(float(line[0]))).zfill(5)
        state = line[1]
        if state in EXCLUDE:
            continue
        # Annual Average (kWh/m2/day)
        value = round(parseNumber(line[2]), 3)
        if zipcode in zipcodes:
            lnglat = zipcodes[zipcode]
            key = "%s,%s" % lnglat
            if key in data:
                data[key].append(value)
            else:
                data[key] = [value]
        # else:
        #     print "Warning: could not find zipcode %s" % zipcode

rows = []
for key in data:
    entries = data[key]
    lnglat = [int(l) for l in key.split(",")]
    value = round(mean(entries), 3)
    rows.append([lnglat[0], lnglat[1], value])

with open(OUTPUT_FILE, 'wb') as f:
    w = csv.writer(f, delimiter=',')
    w.writerow(['lng', 'lat', 'value'])
    for row in rows:
        w.writerow(row)

print "Wrote %s rows to %s" % (len(rows), OUTPUT_FILE)
