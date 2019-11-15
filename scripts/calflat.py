#!/usr/bin/env python
# python3 OK

import focasifu as fi
from bias_overscan import bias_overscan
from flat_combine import flat_combine
from identify_gap import identify_gap
from fit_gap_coordinate import fit_gap_coordinate
from mkedgeimage import mkedgeimage
from identify_edge import identify_edge
from fitcoord_edge import fitcoord_edge
import argparse
from astropy.io import fits

def calflat(calflats, rawdatadir='', overwrite=False):
    basenames = ['','']
    combinednames=['','']

    files = calflats.split(',')
    ovfiles=''
    # bias subtraction, overscan region removing,
    # bad pixel retoring, hedear correction
    for f in files:
        ovname, stat = bias_overscan(f, rawdatadir=rawdatadir, \
                                     overwrite=overwrite)
        if stat == True:
            ovfiles=ovfiles+ovname+','
        else:
            return

    # Combining the flat images
    combinedname = flat_combine(ovfiles[:len(ovfiles)-1],\
                                overwrite=overwrite)

    # Identifying gaps
    identify_gap(combinedname, overwrite=overwrite)
        
    # Fitting the gap coordinates
    fit_gap_coordinate(combinedname, overwrite=overwrite)

    # Extracting spectra, creating the edge-strengthen images.
    mkedgeimage(combinedname, overwrite=overwrite)
        
    identify_edge(combinedname, overwrite=overwrite)
    fitcoord_edge(combinedname, overwrite=overwrite)

    return


if __name__ == '__main__':
    # Analize argments
    parser=argparse.ArgumentParser(description='This is the script for calflat frames.')
    parser.add_argument('-o', help='Overwrite flag', dest='overwrite',
                        action='store_true', default=False)
    parser.add_argument('calflats',
        help='calflat FITS files (comma separated)')
    parser.add_argument('-d', help='Raw data directroy', dest='rawdatadir',
                        action='store', default='')
    args = parser.parse_args()

    calflat(args.calflats, rawdatadir=args.rawdatadir,
            overwrite=args.overwrite)
