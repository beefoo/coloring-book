# -*- coding: utf-8 -*-

import svgwrite

# 4.73 metric tons CO2E /vehicle/year
# https://www.epa.gov/energy/ghg-equivalencies-calculator-calculations-and-references#vehicles
VEHICLE_EMISSIONS = 4.73

# 1.06 metric ton CO2 sequestered annually by one acre of average U.S. forest.
# https://www.epa.gov/energy/ghg-equivalencies-calculator-calculations-and-references#pineforests
ACRE_FOREST_SEQUESTERED = 1.06

# Acres of U.S. forests to take one car off the road for a year
forests = int(round(VEHICLE_EMISSIONS / ACRE_FOREST_SEQUESTERED))
print "%s acres of forest necessary." % forests

# (Should be 4)
