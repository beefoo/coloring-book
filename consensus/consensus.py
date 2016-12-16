# -*- coding: utf-8 -*-

import argparse
import re
import svgwrite
from svgwrite import inch, px
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-hand', dest="HAND_FILE", default="data/hand_left.svg", help="Path to input svg hand file")
parser.add_argument('-width', dest="WIDTH", type=int, default=800, help="Width of output file")
parser.add_argument('-pad', dest="PAD", type=int, default=40, help="Padding of output file")
parser.add_argument('-row', dest="PER_ROW", type=int, default=10, help="Hands per row")
parser.add_argument('-overlapx', dest="OVERLAP_X", type=float, default=0.2, help="Percent to overlap horizontally")
parser.add_argument('-overlapy', dest="OVERLAP_Y", type=float, default=0.6, help="Percent to overlap vertically")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/consensus_%s.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
WIDTH = args.WIDTH
PAD = args.PAD
PER_ROW = args.PER_ROW
OVERLAP_X = args.OVERLAP_X
OVERLAP_Y = args.OVERLAP_Y

# 97% of publishing climate scientists believe climate change is due to human activity
# source: http://iopscience.iop.org/article/10.1088/1748-9326/11/4/048002
SCIENTIFIC_CONSENSUS = 97

# 48% of U.S. adults believe climate change is due to human activity
# source: http://www.pewinternet.org/2016/10/04/public-views-on-climate-change-and-climate-scientists/
PUBLIC_VIEW = 48

hand_path_d = None
hand_path_w = 0
hand_path_h = 0
with open(args.HAND_FILE, 'rb') as f:
    contents = f.read().replace('\n', '')

    # find the path data
    match = re.search(r'<path d="(.+)"/>', contents)
    if match:
        hand_path_d = match.group(1)

    # find the width and height
    match = re.search(r'viewBox="0 0 ([0-9\.]+) ([0-9\.]+)"', contents)
    if match:
        hand_path_w = float(match.group(1))
        hand_path_h = float(match.group(2))
        print "Hand dimensions: %s x %s" % (hand_path_w, hand_path_h)

if hand_path_d is None:
    print "No path found in %s" % args.HAND_FILE
    sys.exit(1)

if hand_path_w <= 0 or hand_path_h <= 0:
    print "Could not find width or height in %s" % args.HAND_FILE
    sys.exit(1)

# determine how much to scale by
hand_w = 1.0 * WIDTH / PER_ROW / OVERLAP_X
scale_amount = hand_w / hand_path_w

# determine height


def makeSVG(filename, amount):
    x = 0
    y = something
    ystep = something
    xstep = something
    while amount > 0:
        x = 0
        for i in range(PER_ROW):
            amount -= 1
            if amount <= 0:
                break
            x += xstep
        y -= ystep

makeSVG(args.OUTPUT_FILE % SCIENTIFIC_CONSENSUS, SCIENTIFIC_CONSENSUS)

# filename = args.OUTPUT_FILE % "test"
# dwg = svgwrite.Drawing(filename, size=((WIDTH+PAD*2)*px, (HEIGHT+PAD*2)*px), profile='full')
# g = dwg.add(dwg.g(id="hand", transform="translate(100,100) scale(10) rotate(15)"))
# g.add(dwg.path(d=hand_path_d))
#
# dwg.save()
# print "Saved svg: %s" % filename
