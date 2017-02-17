# -*- coding: utf-8 -*-

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

# Config
DPI = 72
PAD = 0.5 * DPI
WIDTH = 8.5 * DPI - PAD * 2
HEIGHT = 11 * DPI - PAD * 2
HEADER_H = 1.5 * DPI
COLS = 9
CARS = ['svg/car01.svg','svg/car02.svg','svg/car03.svg','svg/car04.svg','svg/car05.svg','svg/car06.svg','svg/car07.svg','svg/car08.svg','svg/car09.svg','svg/car10.svg']
OUTPUT_FILE = 'data/wind.svg'
GUIDES = False

# 4.73 metric tons CO2E /vehicle/year
# https://www.epa.gov/energy/ghg-equivalencies-calculator-calculations-and-references#vehicles
VEHICLE_EMISSIONS = 4.73

# 3,960 metric tons CO2 / wind turbine installed
# https://www.epa.gov/energy/ghg-equivalencies-calculator-calculations-and-references#turbine
WIND_TURBINE_REDUCTIONS = 3960

# Vehicles offset per year per garbage truck of waste recycled instead of landfilled
vehicles = int(round(WIND_TURBINE_REDUCTIONS / VEHICLE_EMISSIONS))
print "%s vehicles offset." % vehicles

# (Should be 837)

# retrieve svg data
carData = svgu.getDataFromSVGs(CARS)
carSetCount = len(CARS)

# Do calculations
rows = int(math.ceil(1.0 * vehicles / COLS))
carsW = 1.0 * WIDTH
carsH = 1.0 * HEIGHT - HEADER_H
cellW = carsW / COLS
cellH = carsH / rows

# Scale paths
for i, car in enumerate(carData):
    carData[i]["id"] = "car%s" % i
    scale = cellW / car["width"]
    carData[i]["scale"] = scale
    carData[i]["strokeW"] = 1.0 / scale
    # carData[i]["paths"] = svgu.scalePaths(car["paths"], scale)

# init svg
dwg = svgwrite.Drawing(OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
dwgCars = dwg.g(id="cars")
dwgGuide = dwg.g(id="guide")

# Add car definitions
for i, car in enumerate(carData):
    dwgCar = dwg.g(id=car["id"])
    for path in car["paths"]:
        dwgCar.add(dwg.path(d=path, stroke_width=car["strokeW"], stroke="#000000", fill="#FFFFFF"))
    dwg.defs.add(dwgCar)

y = PAD + HEADER_H
for row in range(rows):
    x = PAD
    for col in range(COLS):
        i = COLS * row + col
        if i > vehicles:
            break
        # add car
        car = carData[i % carSetCount]
        t = "translate(%s, %s) scale(%s)" % (x, y, car["scale"])
        dwgCar = dwg.g(transform=t)
        dwgCar.add(dwg.use("#"+car["id"]))
        dwgCars.add(dwgCar)
        x += cellW
    y += cellH

dwg.add(dwgCars)
if GUIDES:
    dwg.add(dwgGuide)

dwg.save()
print "Saved svg: %s" % OUTPUT_FILE
