# -*- coding: utf-8 -*-

import argparse
import math
import re
import svgwrite
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-hand', dest="HAND_FILE", default="data/hand_left.svg", help="Path to input svg hand file")
parser.add_argument('-bg', dest="HAND_FILE_BG", default="data/hand_left_bg.svg", help="Path to input svg hand bg file")
parser.add_argument('-width', dest="WIDTH", type=int, default=700, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=int, default=800, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=int, default=120, help="Padding of output file")
parser.add_argument('-row', dest="PER_ROW", type=int, default=10, help="Hands per row")
parser.add_argument('-scale', dest="SCALE", type=float, default=1.5, help="Percent to scale each hand")
parser.add_argument('-rotate', dest="ROTATE", type=float, default=10.0, help="Max degrees to rotate")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/consensus_%s.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
WIDTH = args.WIDTH
HEIGHT = args.HEIGHT
PAD = args.PAD
PER_ROW = args.PER_ROW
SCALE = args.SCALE
ROTATE = args.ROTATE

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

bg_path_d = None
with open(args.HAND_FILE_BG, 'rb') as f:
    contents = f.read().replace('\n', '')

    # find the path data
    match = re.search(r'<path d="(.+)"/>', contents)
    if match:
        bg_path_d = match.group(1)


if hand_path_d is None or bg_path_d is None:
    print "No path found in %s or " % (args.HAND_FILE, args.HAND_FILE_BG)
    sys.exit(1)

if hand_path_w <= 0 or hand_path_h <= 0:
    print "Could not find width or height in %s" % args.HAND_FILE
    sys.exit(1)

# determine rows
max_value = max(SCIENTIFIC_CONSENSUS, PUBLIC_VIEW)
max_rows = math.ceil(1.0 * max_value / PER_ROW)

# determine scale
hand_ratio = (hand_path_w / hand_path_h)
cell_w = 1.0 * WIDTH / PER_ROW
cell_h = 1.0 * HEIGHT / max_rows
hand_w = cell_w * SCALE
hand_h = hand_w * hand_ratio
transform_scale = hand_w / hand_path_w

# determine step
hand_x_step = cell_w - ((hand_w-cell_w) / PER_ROW)
hand_y_step = cell_h - ((hand_h-cell_h) / max_rows)

print "Scale amount: %s" % transform_scale
print "Hand step: (%s, %s)" % (hand_x_step, hand_y_step)
print "Rows: %s" % max_rows

def halton(index, base=3):
    result = 0
    f = 1.0 / base
    i = index
    while i > 0:
      result += f * float(i % base)
      i = math.floor(i / base)
      f = f / float(base)
    return result

def lerp(v1, v2, amount):
    return (v2-v1) * amount + v1

def makeSVG(filename, amount):
    x = 0
    y = 0
    # start y lower for lower value
    if amount < max_value:
        rows = math.ceil(1.0 * amount / PER_ROW)
        diff = max_rows - rows
        y = diff * hand_y_step
    ystep = hand_y_step
    xstep = hand_x_step
    # offset
    first_row = amount % PER_ROW
    first = True
    # init svg
    dwg = svgwrite.Drawing(filename, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
    # make reference paths
    dwg.defs.add(dwg.path(id="hand", d=hand_path_d))
    dwg.defs.add(dwg.path(id="bg", d=bg_path_d, fill="#FFFFFF"))
    direction = 1.0
    while amount > 0:
        cols = PER_ROW
        if first:
            cols = first_row
            first = False
        x = 0
        offsetX = 0
        if direction < 0:
            offsetX = xstep
        for i in range(int(cols)):
            h = halton(amount)
            rotate = lerp(-1*ROTATE, ROTATE, h)
            # add hand
            t = "translate(%s,%s) scale(%s, %s) rotate(%s)" % (x+PAD+offsetX, y+PAD*0.5, transform_scale*direction, transform_scale, rotate)
            g = dwg.add(dwg.g(id="hand%s" % amount, transform=t))
            # g.add(dwg.path(d=bg_path_d, fill="#FFFFFF"))
            # g.add(dwg.path(d=hand_path_d))
            g.add(dwg.use("#bg"))
            g.add(dwg.use("#hand"))
            # step
            amount -= 1
            if amount <= 0:
                break
            x += xstep
        y += ystep
        direction *= -1
    dwg.save()
    print "Saved svg: %s" % filename


makeSVG(args.OUTPUT_FILE % SCIENTIFIC_CONSENSUS, SCIENTIFIC_CONSENSUS)
makeSVG(args.OUTPUT_FILE % PUBLIC_VIEW, PUBLIC_VIEW)
