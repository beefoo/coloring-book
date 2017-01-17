import re

def getDataFromSVG(filename):
    paths = []
    polygons = []
    width = 0
    height = 0
    with open(filename, 'rb') as f:
        contents = f.read().replace('\n', '')
        # find dimensions
        match = re.search(r'viewBox="0 0 ([0-9\.]+) ([0-9\.]+)"', contents)
        if match:
            width = float(match.group(1))
            height = float(match.group(2))
        else:
            print "Warning: could not find dimensions for %s" % filename

        # find the path data
        matches = re.findall(r'\sd="([^"]+)"\s', contents)
        if matches and len(matches):
            paths = list(matches)
        else:
            print "Warning: couldn't find paths in %s" % filename

        # find the polygon data
        matches = re.findall(r'\spoints="([^"]+)"\s', contents)
        if matches and len(matches):
            polygons = list(matches)

    # return data
    return {
        "width": width,
        "height": height,
        "paths": paths,
        "polygons": polygons
    }

def getDataFromSVGs(filenames):
    data = []
    for filename in filenames:
        fileData = getDataFromSVG(filename)
        data.append(fileData)
    return data

def getTransformString(w, h, x, y, sx=1, sy=1, r=0):
    hw = w * 0.5
    hh = h * 0.5
    tx = x - hw * (sx-1)
    ty = y - hh * (sy-1)
    transform = "translate(%s,%s) scale(%s, %s) rotate(%s, %s, %s)" % (tx, ty, sx, sy, r, hw, hh)
    if r==0:
        transform = "translate(%s,%s) scale(%s, %s)" % (tx, ty, sx, sy)
    return transform
