# -*- coding: utf-8 -*-

import argparse
import os
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-width', dest="WIDTH", type=float, default=600, help="Width of output file")
parser.add_argument('-frames', dest="FRAMES", type=int, default=12, help="Amount of frames")
parser.add_argument('-dpi', dest="DPI", type=int, default=150, help="Dots per inch")
parser.add_argument('-output', dest="OUTPUT_FILE", default="output/frames/frame-%s.png", help="Path to output svg file")

# init input
args = parser.parse_args()
FRAMES = args.FRAMES
DPI = args.DPI
