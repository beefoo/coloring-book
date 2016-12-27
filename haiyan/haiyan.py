# -*- coding: utf-8 -*-

import argparse
import math
import re
import svgwrite
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-country', dest="COUNTRY_FILE", default="data/map-philippines.svg", help="Path to input svg country file")
parser.add_argument('-width', dest="WIDTH", type=int, default=800, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=int, default=1036, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=int, default=60, help="Padding of output file")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/haiyan.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
WIDTH = args.WIDTH
HEIGHT = args.HEIGHT
