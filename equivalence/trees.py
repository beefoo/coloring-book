# -*- coding: utf-8 -*-

import svgwrite

# 4.73 metric tons CO2E /vehicle/year
# https://www.epa.gov/energy/ghg-equivalencies-calculator-calculations-and-references#vehicles
VEHICLE_EMISSIONS = 4.73

# 0.039 metric ton CO2 per urban tree seedling planted and grown for 10 years
# https://www.epa.gov/energy/ghg-equivalencies-calculator-calculations-and-references#seedlings
TREE_SEQUESTERED = 0.039

# Number of tree seedlings grown for 10 years to take one car off the road for a year
trees = int(round(VEHICLE_EMISSIONS / TREE_SEQUESTERED))
print "%s trees necessary." % trees

# (Should be 121)
