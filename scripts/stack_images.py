#!/usr/bin/env python

from astropy.io import fits
import sys
from bias_overscan import stack_data

hdl1 = fits.open(sys.argv[1])
hdl2 = fits.open(sys.argv[2])

outhdl = stack_data(hdl1, hdl2)
outhdl.writeto(sys.argv[3])

