#!/usr/bin/env python
# python3 OK

import argparse
from astropy.io import fits
import numpy as np
import os
import focasifu as fi
from extract import extract
from scipy.ndimage.interpolation import shift as imshift

def mkedgeimage(infile, overwrite=False):
    print('\n#############################')
    print('Making an edge-strength image.')

    if not os.path.isdir(fi.chimagedir):
        os.mkdir(fi.chimagedir)

    gapcoef_file = os.path.splitext(infile)[0]+'.gapcoef'
    inhdl = fits.open(infile)
    inhdr = inhdl[0].header
    basename = inhdr['FRAMEID']
    if os.path.isfile(fi.chimagedir + basename+'.ch01edge.fits'):
        if overwrite:
            for i in range(1, 25):
                try:
                    os.remove(fi.chimagedir + basename+'.ch%02dedge.fits'%i)
                except:
                    pass
        else:
            print('\t Extracted frames already exist. ' + fi.chimagedir + \
                  basename + '.ch12dedge.fits')
            print('\t This procedure is skipped.')
            inhdl.close()
            return basename

    cubehdl = extract(inhdl, gapcoef_file)
    inhdl.close()
    
    scidata = cubehdl[0].data
    shiftval = 2.5
    basename = cubehdl[0].header['FRAMEID']
    for i in range(24):
        outdata = np.zeros((scidata.shape[1],scidata.shape[2]), \
                           dtype=np.float32)
        tempdata1 = scidata[i,:,:] - \
                    imshift(scidata[i,:,:], (0.0, shiftval), order=1, \
                            mode='nearest')
        tempdata2 = scidata[i,:,:] - \
                    imshift(scidata[i,:,:], (0.0, -shiftval), order=1, \
                            mode='nearest')
        outdata = tempdata1 + tempdata2
    
        outhdu = fits.PrimaryHDU(data=outdata)
        outhdl = fits.HDUList([outhdu])
        outhdl[0].header = cubehdl[0].header
        
        outfitsname = fi.chimagedir + basename+'.ch%02dedge.fits'%(i+1)
        outhdl.writeto(outfitsname)
        outhdl.close()

    return


if __name__ == '__main__':
    # Analize argments
    parser=argparse.ArgumentParser(description='This is the script for fitting spectrum edge coordinates.')
    parser.add_argument('infile', help='Combined CAL flat image')
    parser.add_argument('-o', help='Overwrite flag', dest='overwrite', action='store_true',default=False)
    args = parser.parse_args()

    mkedgeimage(args.infile, overwrite=args.overwrite)
