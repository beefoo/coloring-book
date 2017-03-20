# -*- coding: utf-8 -*-

import argparse
import os
from PIL import Image
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-from', dest="FROM_IMAGE", default="data/flux-01.png", help="From image")
parser.add_argument('-to', dest="TO_IMAGE", default="data/flux_color-01.png", help="To image")
parser.add_argument('-width', dest="WIDTH", type=int, default=600, help="Width of output file")
parser.add_argument('-frames', dest="FRAMES", type=int, default=12, help="Amount of frames")
parser.add_argument('-dpi', dest="DPI", type=int, default=150, help="Dots per inch")
parser.add_argument('-output', dest="OUTPUT_FILE", default="output/frames/frame-%s.png", help="Path to output svg file")

# init input
args = parser.parse_args()
FRAMES = args.FRAMES
DPI = args.DPI
OUTPUT_FILE = args.OUTPUT_FILE

# retrieve input images
imFrom = Image.open(args.FROM_IMAGE)
imTo = Image.open(args.TO_IMAGE)
pixelsFrom = list(imFrom.getdata())
pixelsTo = list(imTo.getdata())

# calculate dimensions
(sourceW, sourceH) = imFrom.size
destW = args.WIDTH
destH = int(1.0 * destW * sourceH / sourceW)

# make sure dir exists
outputDir = "/".join(OUTPUT_FILE.split("/")[:-1])
if not os.path.exists(outputDir):
    os.makedirs(outputDir)

# make calculations

# init image
pad = len(str(FRAMES))
pixels = [(255,255,255)] * (destW * destH)
for frame in range(FRAMES):
    im = Image.new("RGB", (destW, destH))
    im.putdata(pixels)


    filename = OUTPUT_FILE % str(frame+1).zfill(pad)
    imageBase.save(filename)
