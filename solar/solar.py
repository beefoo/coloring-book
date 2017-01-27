# -*- coding: utf-8 -*-

# Home energy use data source:
# https://www.epa.gov/energy/greenhouse-gases-equivalencies-calculator-calculations-and-references#houseenergy

# Solar panel data source:
# https://www.google.com/get/sunroof which uses:
    # https://www.census.gov/geo/maps-data/data/tiger-data.html
    # https://nsrdb.nrel.gov/
    # http://apps1.eere.energy.gov/sled/#/

import argparse
import math
import os
from pprint import pprint
import sys

# On average, each home consumed 12,183 kWh of delivered electricity (EIA 2015a).
ENERGY_CONSUMED_PER_HOME = 12183

# Project Sunroof data
# https://www.google.com/get/sunroof
CITY_ROOFTOP_DATA = {
    "san_jose": {
        "label": "San Jose, CA",
        "households": 301366, # http://www.census.gov/2010census/popmap/ipmtext.php?fl=06:0668000
        "rooftops": 205000,
        "electricity": 5800000000, # kWh AC per yr
        "source": "https://www.google.com/get/sunroof/data-explorer/place/ChIJ9T_5iuTKj4ARe3GfygqMnbk/"
    },
    "fresno": {
        "label": "Fresno, CA",
        "households": 158349, # http://www.census.gov/2010census/popmap/ipmtext.php?fl=06:0627000
        "rooftops": 148000,
        "electricity": 4800000000, # kWh AC per yr
        "source": "https://www.google.com/get/sunroof/data-explorer/featured/2/fresno"
    },
    "oklahoma_city": {
        "label": "Oklahoma City, OK",
        "households": 230233, # http://www.census.gov/2010census/popmap/ipmtext.php?fl=4055000
        "rooftops": 200000,
        "electricity": 5300000000, # kWh AC per yr
        "source": "https://www.google.com/get/sunroof/data-explorer/featured/1/oklahoma-city"
    },
    "san_francisco": {
        "label": "San Francisco, CA",
        "households": 345811, # http://www.census.gov/2010census/popmap/ipmtext.php?fl=0667000
        "rooftops": 123000,
        "electricity": 2400000000, # kWh AC per yr
        "source": "https://www.google.com/get/sunroof/data-explorer/place/ChIJIQBpAG2ahYAR_6128GcTUEo/"
    }
}

# Make calculations
data = CITY_ROOFTOP_DATA.copy()
for key, d in CITY_ROOFTOP_DATA.iteritems():
    data[key]["electricityPerHousehold"] = int(round(1.0 * d["electricity"] / d["rooftops"]))
    forHouseholds = int(round(1.0 * d["electricity"] / ENERGY_CONSUMED_PER_HOME))
    data[key]["surplusHousholds"] = int(forHouseholds - d["rooftops"])
    data[key]["percentSurplus"] = int(round(1.0 * forHouseholds / d["rooftops"] * 100))
    data[key]["citySurplusHouseholds"] = int(forHouseholds - d["households"])
    data[key]["cityPercentSurplus"] = int(round(1.0 * forHouseholds / d["households"] * 100))
    data[key]["forHouseholds"] = forHouseholds

# Print report
for key, d in data.iteritems():
    print "%s:" % d["label"]
    print " - %s rooftops" % "{:,}".format(d["rooftops"])
    print " - %s kWh/year/household" % "{:,}".format(d["electricityPerHousehold"])
    print " - enough electricity for %s households" % "{:,}".format(d["forHouseholds"])
    print " - %s (+%s%%) surplus households" % ("{:,}".format(d["surplusHousholds"]), d["percentSurplus"])
    print " - %s city households" % "{:,}".format(d["households"])
    if d["citySurplusHouseholds"] > 0:
        print " - %s (+%s%%) city surplus households" % ("{:,}".format(d["citySurplusHouseholds"]), d["cityPercentSurplus"])
    print "-----"

# Define what we want to display
source = data["fresno"]
destination = data["san_francisco"]

# Display how much energy is supplied for destination from source
percentSupplied = int(round(1.0 * source["forHouseholds"] / destination["households"] * 100))
print "%s creates energy for %s households" % (source["label"], "{:,}".format(source["forHouseholds"]))
print "%s has %s households (%s%% supplied w/ energy from %s)" % (destination["label"], "{:,}".format(destination["households"]), percentSupplied, source["label"])
print "%s has %s%% households of %s" % (destination["label"], int(round(1.0*destination["households"]/source["households"]*100)), source["label"])
