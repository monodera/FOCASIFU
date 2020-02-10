#!/usr/bin/env python
# python3 OK

import argparse
from astropy.io import fits
import numpy as np
import sys
import os
import focasifu as fi
from pyraf import iraf


def fluxcalib_each(infile, outfile, sens, overwrite=False):
    if not fi.check_version_f(infile):
        return outfile, False
    if os.path.isfile(outfile) and not overwrite:
        print('\t Flux calibrated file already exits. '+outfile)
        print('\t This procedure is skipped.')
        return outfile, True
    if os.path.isfile(outfile) and overwrite:
        try:
            os.remove(outfile)
        except:
            pass
            
    tempfile = iraf.mktemp('tmp_')
    iraf.fluxcalib(infile, tempfile, sens, exposure='EXPTIME')
    
    iraf.extinct(tempfile, outfile, extinct=fi.filibdir+'mkoextinct.dat')
    try:
        os.remove(tempfile+'.fits')
    except:
        pass
    
    return outfile, True


def fluxcalib(inid, sens, overwrite=False):
    print('\n#############################')
    print('Flux calibration\n')

    for i in range(1,25):
        infile = fi.chimagedir + inid + '.ch{:02d}.wc.fits'.format(i)
        outfile= fi.chimagedir + inid + '.ch{:02d}.fc.fits'.format(i)
        outfile, stat = fluxcalib_each(infile, outfile, sens,
                                        overwrite=overwrite)
        if not stat:
            print('Error in flux calibration: '+infile +'->' +outfile)
            return outfile, False

    return outfile, True
        
if __name__ == '__main__':
    # Analize argments
    parser=argparse.ArgumentParser(description=\
                'This is the reduction script for an object frame.')
    parser.add_argument('inid', help='Frame ID')
    parser.add_argument('sens', help='Sensitifity function image name.')
    parser.add_argument('-o', help='Overwrite flag', dest='overwrite',\
                        action='store_true',default=False)
    args = parser.parse_args()

    fluxcalib(args.inid, args.sens, overwrite=args.overwrite)
