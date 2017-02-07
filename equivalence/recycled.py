# -*- coding: utf-8 -*-

import svgwrite

# 4.73 metric tons CO2E /vehicle/year
# https://www.epa.gov/energy/ghg-equivalencies-calculator-calculations-and-references#vehicles
VEHICLE_EMISSIONS = 4.73

# 22.06 metric tons CO2E /garbage truck of waste recycled instead of landfilled
# https://www.epa.gov/energy/ghg-equivalencies-calculator-calculations-and-references#garbagetruck
RECYCLED_TRUCK_REDUCTIONS = 22.06

# Vehicles offset per year per garbage truck of waste recycled instead of landfilled
vehicles = int(round(RECYCLED_TRUCK_REDUCTIONS / VEHICLE_EMISSIONS))
print "One garbage truck of waste recycled instead of landfilled is equivalent to taking %s cars off the road for one year." % vehicles

# (Should be 5)
