# -*- coding: utf-8 -*-

import argparse
import os
from PIL import Image
import sys

# Usage:
#   python color_timelapse.py -output "output/flux-diagonal/frame-%s.jpg" -sort diagonal
#   ffmpeg -f image2 -framerate 6 -i output/flux-diagonal/frame-%02d.jpg -vf scale=600x464 output/flux-diagonal.gif
#   python color_timelapse.py -output "output/flux-horizontal/frame-%s.jpg" -sort horizontal
#   ffmpeg -f image2 -framerate 6 -i output/flux-horizontal/frame-%02d.jpg -vf scale=600x464 output/flux-horizontal.gif

# input
parser = argparse.ArgumentParser()
parser.add_argument('-from', dest="FROM_IMAGE", default="data/flux-01.png", help="From image")
parser.add_argument('-to', dest="TO_IMAGE", default="data/flux_color-01.png", help="To image")
parser.add_argument('-frames', dest="FRAMES", type=int, default=12, help="Amount of frames")
parser.add_argument('-sort', dest="SORT", default="diagonal", help="diagonal, horizontal")
parser.add_argument('-output', dest="OUTPUT_FILE", default="output/frames/frame-%s.jpg", help="Path to output svg file")

# init input
args = parser.parse_args()
FRAMES = args.FRAMES
SORT = args.SORT
OUTPUT_FILE = args.OUTPUT_FILE

# retrieve input images
imFrom = Image.open(args.FROM_IMAGE)
imTo = Image.open(args.TO_IMAGE)
pixelsFrom = list(imFrom.getdata())
pixelsTo = list(imTo.getdata())

# check to see if image dimensions match
if len(pixelsFrom) != len(pixelsTo):
    print "Dimensions mismatch"
    sys.exit(1)

# calculate dimensions
(w, h) = imFrom.size
print "Dimensions: %s x %s" % (w, h)

# get diff pixels
diff = []
for i, p0 in enumerate(pixelsFrom):
    p1 = pixelsTo[i]
    if p0 != p1:
        row = i / w
        col = i % w
        diff.append({
            "index": i,
            "pixel": p1,
            "row": row,
            "col": col
        })
diffLen = len(diff)
if diffLen <= 0:
    print "Images are the same!"
    sys.exit(1)

# make sure dir exists
outputDir = "/".join(OUTPUT_FILE.split("/")[:-1])
if not os.path.exists(outputDir):
    os.makedirs(outputDir)

# sort pixels
if SORT == "horizontal":
    diff = sorted(diff, key=lambda k: k["index"])

elif SORT == "diagonal":
    diff = sorted(diff, key=lambda k: k["row"] + k["col"])

# init image
zeroPad = len(str(FRAMES))
for frame in range(FRAMES):
    pixels = pixelsFrom[:]
    # get the pixel diff for this frame
    progress = 1.0 * frame / (FRAMES-1)
    diffAmount = int(round(progress * diffLen))
    frameDiff = diff[:diffAmount]

    # override old pixels
    for d in frameDiff:
        i = d["index"]
        p = d["pixel"]
        pixels[i] = p

    # write pixels to image
    im = Image.new("RGB", (w, h))
    im.putdata(pixels)
    filename = OUTPUT_FILE % str(frame+1).zfill(zeroPad)
    im.save(filename)
    print "Saved %s" % filename
