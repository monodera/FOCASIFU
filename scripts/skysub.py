#!/usr/bin/env python3
# python3 OK

from astropy.io import fits
import numpy as np
import os
import argparse
import focasifu as fi
from scipy.ndimage.interpolation import shift as imshift


def skysub(infile, comp, x1=53, x2=62, scale=1.0, overwrite=False):
    print('\n#############################')
    print('Sky subtraction')
    hdl = fits.open(infile)
    basename = hdl[0].header['FRAMEID']
    outfile = basename + '.ss.fits'
    
    if not fi.check_version(hdl):
        return outfile, False
    
    if os.path.isfile(outfile):
        if not overwrite:
            print('\t Sky subtracted file already exits. '+outfile)
            print('\t This procedure is skipped.')
            return outfile, True
        
    scidata = hdl[0].data

    dy = np.loadtxt(comp+'.sky_shift.dat')

    # Maiking 1D sky spectrum
    temp =np.mean(scidata[:,23,x1-1:x2],axis=1)
    # Because scipy.ndimage.interpolation.shift can not deal with NaN,
    # NaN is replaced to zero.
    temp2 = np.nan_to_num(temp)
    sky1d = temp2*scale

    # Subtracting sky spectrum.
    print('\t Subtracting the sky specturm.')
    outdata = np.zeros(scidata.shape, dtype=np.float32)
    for i in range(scidata.shape[1]):
        for j in range(scidata.shape[2]):
            sky1d_shifted = imshift(sky1d, dy[i,j], order=5, mode='nearest')
            outdata[:,i,j] = scidata[:,i,j] - sky1d_shifted

    # Writing the output file
    outhdu = fits.PrimaryHDU(outdata)
    outhdl = fits.HDUList([outhdu])
    outhdl[0].header = hdl[0].header
    outhdl[0].header['SKY_X1'] = (x1, 'Start pixel for sky spectrum')
    outhdl[0].header['SKY_X2'] = (x2, 'End pixel for sky spectrum')
    outhdl[0].header['SKY_SCL'] = (scale, 'Scale factor for sky spectrum')
    outhdl.writeto(outfile, overwrite=overwrite)
    outhdl.close()
    hdl.close()
    print('\t Sky subtracted file: '+outfile)
    return outfile, True


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='This is the '+\
            'script for subtracting the sky background spectrum.')
    parser.add_argument('-o', help='Overwrite flag', dest='overwrite',\
            action='store_true',default=False)
    parser.add_argument('infile', help='Input FITS file.')
    parser.add_argument('comp', help='Comparison ID.')
    parser.add_argument('-x1', help='Start pixel for integrating '+\
            'the sky spectrum. (default: 53)', default=53, type=int)
    parser.add_argument('-x2', help='End pixel for integrating '+\
            'the sky spectrum. (default: 62)', default=62, type=int)
    parser.add_argument('-scale', help='Scale factor applied for '+\
            'the sky spectrum. (default: 1.0)', default=1.0, type=float)
    args = parser.parse_args()

    skysub(args.infile, args.comp, x1=args.x1, x2=args.x2, \
           scale=args.scale, overwrite=args.overwrite)
