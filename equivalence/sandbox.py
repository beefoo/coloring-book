# -*- coding: utf-8 -*-

import cmath
import inspect
import math
import os
from pprint import pprint
import svgwrite
import sys

# add parent directory to sys path to import relative modules
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import lib.svgutils as svgu
from lib.path import CubicBezier, Line, QuadraticBezier

svgData = svgu.getParsedDataFromSVG("svg/tree01.svg")

print "W: %s, H: %s" % (svgData["width"], svgData["height"])

path = svgData["paths"][0]

pprint(path)
