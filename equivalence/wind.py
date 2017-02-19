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
import lib.mathutils as mu

# Config
DPI = 72
PAD = 0.5 * DPI
WIDTH = 8.5 * DPI - PAD * 2
HEIGHT = 11 * DPI - PAD * 2
HEADER_H = 1.5 * DPI
COLS = 9
OSC_X = 0.25 * DPI
OSC_Y = 0.25 * DPI
OSC_FREQ = 2.0
OSC_ANGLE = 15.0
CARS = ['svg/car01b.svg','svg/car06b.svg','svg/car09b.svg','svg/car10b.svg']
OUTPUT_FILE = 'data/wind.svg'
GUIDES = True

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
carsW = 1.0 * WIDTH - OSC_X * 2
carsH = 1.0 * HEIGHT - HEADER_H - OSC_Y * 2
cellW = carsW / (COLS+0.5)
cellH = carsH / rows

# Scale paths
for i, car in enumerate(carData):
    carData[i]["id"] = "car%s" % i
    scale = cellW / car["width"] * 0.9
    carData[i]["scale"] = scale
    carData[i]["strokeW"] = 1.0 / scale
    # carData[i]["paths"] = svgu.scalePaths(car["paths"], scale)

# init svg
dwg = svgwrite.Drawing(OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
dwgCars = dwg.g(id="cars")
dwgGuide = dwg.g(id="guide")
dwgTurbine = dwg.g(id="turbine")

# Add car definitions
for i, car in enumerate(carData):
    dwgCar = dwg.g(id=car["id"])
    for path in car["paths"]:
        dwgCar.add(dwg.path(d=path, stroke_width=car["strokeW"], stroke="#000000", fill="#FFFFFF"))
    dwg.defs.add(dwgCar)

offsetY = PAD + HEADER_H + OSC_Y
offsetX = PAD + OSC_X
y = offsetY
carPoints = []
for row in range(rows):
    x = offsetX
    for col in range(COLS):
        i = COLS * row + col
        if i > vehicles:
            break
        # oscillation
        car = carData[i % carSetCount]
        dx = mu.oscillate(1.0 * row / (rows-1), OSC_X, OSC_FREQ) - car["width"] * car["scale"] * 0.33
        dy = mu.oscillate(1.0 * col / (COLS-1), OSC_Y, OSC_FREQ) - car["height"] * car["scale"] * 1.2
        angle = mu.oscillate(1.0 * col / (COLS-1), OSC_ANGLE, OSC_FREQ)
        if row % 2 > 0:
            dx += cellW * 0.5
        carPoints.append(["#"+car["id"], (car["width"], car["height"], x+dx, y+dy, car["scale"], angle)])
        x += cellW
    y += cellH

# sort points
carPoints = sorted(carPoints, key=lambda cp: cp[1][3])

for cp in carPoints:
    # add car
    p = cp[1]
    t = svgu.getTransformString(p[0], p[1], p[2], p[3], p[4], p[4], p[5])
    dwgCar = dwg.g(transform=t)
    dwgCar.add(dwg.use(cp[0]))
    dwgCars.add(dwgCar)

# turbine
TURBINE_W = 0.33 * DPI
offsetY = PAD + HEADER_H
offsetX = PAD + WIDTH * 0.5 - TURBINE_W * 0.5
y = offsetY
turbineL = []
turbineR = []
for row in range(rows):
    x = offsetX
    dx = mu.oscillate(1.0 * row / (rows-1), OSC_X, OSC_FREQ)
    turbineL.append((x+dx, y))
    turbineR = [(x+dx+TURBINE_W, y)] + turbineR
    y += cellH
turbineLCommands = svgu.pointsToCurve(turbineL, 0.5)
turbineRCommands = svgu.pointsToCurve(turbineR, 0.5)
turbineLCommands.append("L%s,%s" % turbineR[0])
turbinePath = turbineLCommands + turbineRCommands[1:] + ["Z"]
dwgTurbine.add(dwg.path(d=turbinePath, stroke_width=2, stroke="#000000", fill="#FFFFFF"))

dwgGuide.add(dwg.rect(insert=(PAD,PAD), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))

dwg.add(dwgCars)
if GUIDES:
    dwg.add(dwgGuide)
dwg.add(dwgTurbine)

dwg.save()
print "Saved svg: %s" % OUTPUT_FILE
