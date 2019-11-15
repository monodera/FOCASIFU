#!/usr/bin/env python

import argparse
from astropy.io import fits
from bias_overscan import bias_subtraction

parser=argparse.ArgumentParser(description='This is the script for bias subtraction.')
parser.add_argument('ifname',
                    help='Input FITS file name')
parser.add_argument('ofname',
                    help='Output FITS file name')    
parser.add_argument('-d', help='Raw data directroy', dest='rawdatadir',
                    action='store', default='')
parser.add_argument('-o', help='Overwrite flag', dest='overwrite',
                    action='store_true', default=False)
args = parser.parse_args()

hdl = fits.open(args.rawdatadir + args.ifname)
newhdl = bias_subtraction(hdl)
hdl.close()
if newhdl != False:
    newhdl.writeto(args.ofname, overwrite=args.overwrite)
    newhdl.close()

