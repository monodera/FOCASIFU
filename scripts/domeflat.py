#!/usr/bin/env python
# python3 OK

import focasifu as fi
from bias_overscan import bias_overscan
from flat_combine import flat_combine
from divhighlow import divhighlow
import argparse
from astropy.io import fits

def domeflat(domeflats, rawdatadir='', overwrite=False):
    files = domeflats.split(',')
    ovfiles=''
    # bias subtraction, overscan region removing, bad pixel retoring,
    # hedear correction
    for f in files:
        ovname, stat = bias_overscan(f, rawdatadir=rawdatadir, \
                                     overwrite=overwrite)
        if stat == True:
            ovfiles=ovfiles+ovname+','
        else:
            return
        
    # Combining the flat images
    combinedname = flat_combine(ovfiles[:len(ovfiles)-1], \
                                       overwrite=overwrite)
    # Dividing the flat frame into high and low frequency components.
    divhighlow(combinedname, overwrite=overwrite)

    return


if __name__ == '__main__':
    # Analize argments
    parser=argparse.ArgumentParser(description='This is the script for '+\
                                   'making a combined domeflat frame.')
    parser.add_argument('-o', help='Overwrite flag', dest='overwrite', \
                        action='store_true',default=False)
    parser.add_argument('-d', help='Raw data directroy', dest='rawdatadir', \
                        action='store', default='')
    parser.add_argument('domeflats', help='Domeflat frames for Chip1 '+\
                        '(comma separated)')
    args = parser.parse_args()
    domeflat(args.domeflats, rawdatadir=args.rawdatadir, \
             overwrite=args.overwrite)

