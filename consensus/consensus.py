# -*- coding: utf-8 -*-

import argparse
import re
import svgwrite
from svgwrite import inch, px

# input
parser = argparse.ArgumentParser()
parser.add_argument('-hand', dest="HAND_FILE", default="data/hand_left.svg", help="Path to input svg hand file")
parser.add_argument('-width', dest="WIDTH", type=int, default=800, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=int, default=800, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=int, default=40, help="Padding of output file")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/consensus_%s.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
WIDTH = args.WIDTH
HEIGHT = args.HEIGHT
PAD = args.PAD

# 97% of publishing climate scientists believe climate change is due to human activity
# source: http://iopscience.iop.org/article/10.1088/1748-9326/11/4/048002
SCIENTIFIC_CONSENSUS = 97

# 48% of U.S. adults believe climate change is due to human activity
# source: http://www.pewinternet.org/2016/10/04/public-views-on-climate-change-and-climate-scientists/
PUBLIC_VIEW = 48

hand_path_d = ""
with open(args.HAND_FILE, 'rb') as f:
    contents = f.read()
    match = re.search(r'<path d\=\"(.+)\"\/>', contents)
    if match:
        hand_path_d = match.group(1)
    else:
        print "Warning: No path found in %s" % args.HAND_FILE

filename = args.OUTPUT_FILE % "test"
dwg = svgwrite.Drawing(filename, size=((WIDTH+PAD*2)*px, (HEIGHT+PAD*2)*px), profile='full')
g = dwg.add(dwg.g(id="hand", transform="translate(100,100) scale(10) rotate(15)"))
g.add(dwg.path(d=hand_path_d))

dwg.save()
print "Saved svg: %s" % filename
