# -*- coding: utf-8 -*-

import math
from shared import getDataFromSVGs
from shared import getTransformString
import svgwrite

# Config
PAD = 100
CARS = ['svg/car01.svg','svg/car02.svg','svg/car03.svg','svg/car04.svg','svg/car05.svg','svg/car06.svg','svg/car07.svg','svg/car08.svg','svg/car09.svg','svg/car10.svg']
OUTPUT_FILE = 'data/wind.svg'
GUIDES = False

# Spiral config
THETA_START = 10.0
SPIRAL_A = 0 # turns the spiral
SPIRAL_B = 5 # controls the distance between successive turnings.
SPIRAL_STEP = 50

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
carData = getDataFromSVGs(CARS)
carSetCount = len(CARS)

# Add more tree data
for i, car in enumerate(carData):
    carData[i]["id"] = "car%s" % i
    carData[i]["scale"] = 1.0 * SPIRAL_STEP / car["width"] * 1.5

# determine the width of the svg
maxRadius = 0
theta = THETA_START
x = 0
y = 0
a = SPIRAL_A
b = SPIRAL_B
for i in range(vehicles):
    r = a + b * theta
    x = r * math.cos(theta)
    y = r * math.sin(theta)
    d = math.hypot(x, y)
    a = math.acos((2.0 * math.pow(d,2) - math.pow(SPIRAL_STEP,2)) / (2.0 * math.pow(d,2)))
    theta += a
    maxRadius = max([maxRadius, abs(x), abs(y)])
width = int(math.ceil(maxRadius * 2))
height = width
print "Width: %s" % width
cx = width * 0.5
cy = height * 0.5

# init svg
dwg = svgwrite.Drawing(OUTPUT_FILE, size=(width+PAD*2, height+PAD*2), profile='full')
dwgCars = dwg.g(id="cars")
dwgGuide = dwg.g(id="guide")

# Add car definitions
for i, car in enumerate(carData):
    dwgCar = dwg.g(id=car["id"])
    for path in car["paths"]:
        dwgCar.add(dwg.path(d=path, stroke_width=1, stroke="#000000", fill="#FFFFFF"))
    dwg.defs.add(dwgCar)

# draw car spiral
theta = THETA_START
a = SPIRAL_A
b = SPIRAL_B
for i in range(vehicles):
    r = a + b * theta
    x = cx + r * math.cos(theta)
    y = cy + r * math.sin(theta)
    d = math.hypot(x - cx, y - cy)
    a = math.acos((2.0 * math.pow(d,2) - math.pow(SPIRAL_STEP,2)) / (2.0 * math.pow(d,2)))
    theta += a
    # add car
    car = carData[i % carSetCount]
    t = getTransformString(car["width"], car["height"], x-car["width"]*0.5+PAD, y-car["height"]*0.5+PAD, car["scale"], car["scale"])
    carWrapper = dwg.g(transform=t)
    carWrapper.add(dwg.use("#"+car["id"]))
    dwgCars.add(carWrapper)
    if GUIDES:
        dwgGuide.add(dwg.circle(center=(x+PAD, y+PAD), r=2, fill="black"))

dwg.add(dwgCars)
if GUIDES:
    dwg.add(dwgGuide)
dwg.save()
print "Saved svg: %s" % OUTPUT_FILE
