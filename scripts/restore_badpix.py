#!/usr/bin/env python

from astropy.io import fits
from bias_overscan import restore_badpix
import sys

inhdl = fits.open(sys.argv[1])
outhdl, stat = restore_badpix(inhdl)
outhdl.writeto(sys.argv[2])
inhdl.close()
outhdl.close()
    
