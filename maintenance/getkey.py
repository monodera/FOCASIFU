#!/usr/bin/env python
#
# This is the script for making a mask image
# for the decomposition of a dome flat image.
#
# badpixposition.py flat_fcmb.fits dust.fits -h high.fits
#
from pyds9 import *

def getkey():
    DS9list = ds9_targets()

    if DS9list is None:
        d = DS9()
    else:
        d = DS9(DS9list[0])

    a = d.get('iexam key coordinate image')
    b = a.split()
    key = b[0]
    x = int(float(b[1])+0.5)
    y = int(float(b[2])+0.5)
    print(key, x, y)
    return

if __name__ == '__main__':
    getkey()

