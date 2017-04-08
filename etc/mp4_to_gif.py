# -*- coding: utf-8 -*-

import argparse
import os
import subprocess
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-in', dest="INPUT_FILE", default="input/flux_01.mp4", help="Path to .mp4 file")
parser.add_argument('-frames', dest="FRAMES", type=int, default=20, help="Number of frames")
parser.add_argument('-size', dest="SIZE", default="640x360", help="Size of gif")
parser.add_argument('-rate', dest="FRAMERATE", type=int, default=10, help="Frame rate")
parser.add_argument('-out', dest="OUTPUT_DIR", default="output/", help="Output directory")

# init input
args = parser.parse_args()
INPUT_FILE = args.INPUT_FILE
FRAMES = args.FRAMES
SIZE = args.SIZE
FRAMERATE = args.FRAMERATE
OUTPUT_DIR = args.OUTPUT_DIR

def getLength(filename):
    result = subprocess.Popen('ffprobe -i %s -show_entries format=duration -v quiet -of csv="p=0"' % filename, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = result.communicate()
    return float(output[0])

zeroPad = len(str(FRAMES))
duration = getLength(INPUT_FILE)

# Generate frames
tmpFiles = []
for frame in range(FRAMES):
    p = 1.0 * frame / (FRAMES-1)
    time = duration * p
    # if last frame subtract fraction of second
    if p >= 1:
        time = duration - 0.1
    tmpFile = OUTPUT_DIR + "frame-%s.jpg" % str(frame).zfill(zeroPad)
    # command = "ffmpeg -ss %s -i %s -t 1 -s %s -f image2 %s" % (time, INPUT_FILE, SIZE, tmpFile)
    command = "ffmpeg -ss %s -i %s -vframes 1 -s %s %s -loglevel panic" % (time, INPUT_FILE, SIZE, tmpFile)
    print command
    command = command.split(" ")
    finished = subprocess.check_call(command)
    tmpFiles.append(tmpFile)

# Create gif
filename = INPUT_FILE.split("/")[-1].split(".")[0]
outputFile = OUTPUT_DIR + filename + ".gif"
inputFiles = OUTPUT_DIR + "frame-%%0%sd.jpg" % zeroPad
command = "ffmpeg -f image2 -framerate %s -i %s -vf scale=%s %s -loglevel panic" % (FRAMERATE, inputFiles, SIZE, outputFile)
print command
command = command.split(" ")
finished = subprocess.check_call(command)

# Remove temp files
for tmpFile in tmpFiles:
    os.remove(tmpFile)

print "Done."
