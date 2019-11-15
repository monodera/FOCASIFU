#!/usr/bin/env python

from bias_overscan import remove_overscan
from astropy.io import fits
import sys

if __name__ == '__main__':
    hdl = fits.open(sys.argv[1])
    newhdl, stat = remove_overscan(hdl)
    newhdl.writeto(sys.argv[2])
    hdl.close()
    newhdl.close()
