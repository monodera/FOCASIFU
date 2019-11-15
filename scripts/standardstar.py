#!/usr/bin/env python
# python3 OK

import focasifu as fi
import argparse
from bias_overscan import bias_overscan
from cosmicrays import cosmicrays
from mkchimage import mkchimage
from flatfielding import flatfielding
from transform import transform
from fluxcalib import fluxcalib
from mkcube import mkcube
from skysub import skysub
from std1dspec import std1dspec
from standard_sens import standard_sens

def standardstar(infile, domeflat=None, domecomp=None, calflat=None, \
                 comparison=None, rawdatadir='', overwrite=False):
    print('\n#############################')
    print('#############################')
    print('Reducing the standard star frame')

    basenames=['','']
    # bias subtraction, overscan region removing,
    # bad pixel retoring, hedear correction
    ovname, stat = bias_overscan(infile, rawdatadir=rawdatadir,
                                 overwrite=overwrite)
    if stat == False:
        return ovname, False

    # cosmicray removing
    crname, maskname, stat = cosmicrays(ovname, overwrite=overwrite)
    if stat == False:
        return crname, False

    # flat fielding
    bias_overscan(domecomp+'.fits', rawdatadir=rawdatadir,
                      overwrite=overwrite)
    ffname, stat = flatfielding(crname, domeflat, calflat, domecomp,
                                comparison, overwrite=overwrite)
    if stat == False:
        return ffname, False

    # extraction and making each channel image
    basename, stat = mkchimage(ffname, calflat, overwrite=overwrite)
    if stat == False:
        return basename, False
    
    # Transorming
    stat = transform(basename, comparison, calflat, overwrite=overwrite)
    if stat == False:
        return '', False
            
    # Making data cube
    cubefile, stat = mkcube(basename, 'wc', overwrite=overwrite)
    if stat == False:
        return cubefile, False

    # Sky subtraction
    skysubedfile, stat = skysub(cubefile, overwrite=overwrite)
    if stat == False:
        return skysubedfile, False

    # Making 1D spectrum of the standard star
    std1dspecfile, stat = std1dspec(skysubedfile, overwrite=overwrite)
    if stat == False:
        return
    
    # Deriving sensitivity function
    sensfile, stat = standard_sens(std1dspecfile, caldir='onedstds$add/', \
                            overwrite=overwrite)
    if stat == False:
        return

    return


if __name__ == '__main__':
    # Analize argments
    parser=argparse.ArgumentParser(description=\
                'This is the reduction script for an object frame.')
    parser.add_argument('infile', help='Input file name')
    parser.add_argument('dflat', help='Domeflat frame ID')
    parser.add_argument('cflat', help='Calflat frame ID')
    parser.add_argument('comp', help='Comparison frame ID')
    parser.add_argument('domecompid', help='Comparison frame ID for domeflat')
    parser.add_argument('-d', help='Raw data directroy', \
                        dest='rawdatadir', action='store', default='')
    parser.add_argument('-o', help='Overwrite flag', dest='overwrite',\
                        action='store_true',default=False)
    args = parser.parse_args()
    
    standardstar(args.infile, domeflat=args.dflat, domecomp=args.domecompid,\
                 calflat=args.cflat, comparison=args.comp,\
                 rawdatadir = args.rawdatadir, overwrite = args.overwrite)
