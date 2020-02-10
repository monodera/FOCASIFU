#!/usr/bin/env python
# python3 OK

import argparse
from bias_overscan import bias_overscan
from cosmicrays import cosmicrays
from mkchimage import mkchimage
from flatfielding import flatfielding
from transform import transform
from fluxcalib import fluxcalib
from mkcube import mkcube
from skysub import skysub


def object(infile, domeflat=None, domecomp=None, calflat=None,
           comparison=None, comparison2=None, stdstar=None,
           rawdatadir='', overwrite=False):
    print('\n#############################')
    print('#############################')
    print('Reducing the object frame')

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
                                comparison2, overwrite=overwrite)
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
            
    # Flux calibration
    if stdstar is not None and stdstar != 'None':
        fcfile, stat = fluxcalib(basename, stdstar+'.sens.fits', \
                                 overwrite=overwrite)
        postfix = 'fc'
        if stat == False:
            return fcfile, False
    else:
        postfix = 'wc'
            
    # Making data cube
    cubefile, stat = mkcube(basename, postfix, overwrite=overwrite)
    if stat == False:
        return cubefile, False

    # Sky subtraction
    skysubedfile, stat = skysub(cubefile, overwrite=overwrite)
    if stat == False:
        return skysubedfile, False

    return skysubedfile, True

if __name__ == '__main__':
    # Analize argments
    parser=argparse.ArgumentParser(description='This is the reduction'+\
                                   'script for an object frame.')
    parser.add_argument('infile', help='Input FITS file')
    parser.add_argument('dflatid', help='Domeflat frame ID')
    parser.add_argument('cflatid', help='Calflat frame ID')
    parser.add_argument('compid', help='Comparison frame ID')
    parser.add_argument('compid2', help='Comparison frame ID')
    parser.add_argument('domecompid', help='Comparison frame ID for domeflat')
    parser.add_argument('stdstarid', help='Standard star frame ID')
    parser.add_argument('-d', help='Raw data directroy', dest='rawdatadir', 
                        action='store', default='')
    parser.add_argument('-o', help='Overwrite flag', dest='overwrite', 
                        action='store_true',default=False)
    args = parser.parse_args()
    
    object(args.infile, domeflat=args.dflatid, domecomp=args.domecompid,
           calflat=args.cflatid, comparison=args.compid,
           comparison2=args.compid2, stdstar = args.stdstarid,
           rawdatadir = args.rawdatadir, overwrite = args.overwrite)
