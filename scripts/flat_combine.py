#!/usr/bin/env python
# python3 OK

import focasifu as fi
import argparse
from astropy.io import fits
import os
import sys
from pyraf import iraf

def flat_combine(infiles_comma, overwrite=False):
    print('\n#############################')
    print('Combining the flat frames.')
    infiles = infiles_comma.split(',')
    combinedname = fits.getval(infiles[0],'FRAMEID')+'.fcmb.fits'
    if os.path.exists(combinedname):
        if overwrite:
            try:
                os.remove(combinedname)
            except:
                pass
        else:
            print('\t Combined flat frame already exists. '+combinedname)
            print('\t This precedure is skipped.')
            return combinedname
    iraf.imcombine(infiles_comma, combinedname, combine='median', reject='no')

    return combinedname


if __name__ == '__main__':
    # Analize argments
    parser=argparse.ArgumentParser(description=\
            'This is the reduction script for combining flat frames.')
    parser.add_argument('infiles', help='Comma-separated input file names')
    parser.add_argument('-o', help='Overwrite flag', dest='overwrite', action='store_true',default=False)
    args = parser.parse_args()

    flat_combine(args.infiles, overwrite=args.overwrite)


