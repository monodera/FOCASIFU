#!/usr/bin/env python
# python3 OK

import os
import focasifu as fi
import argparse
import numpy as np
from astropy.io import fits
import astroscrappy 

def cosmicrays(infile, sigclip=5.0, sigfrac=0.2, objlim=2.0, niter = 4, \
               overwrite=False):
    print('\n#############################')
    print('Cosmicray removing.')

    inhdl = fits.open(infile)
    inhdr = inhdl[0].header
    scidata = inhdl[0].data
    basename = inhdr['FRAMEID']
    crname = basename+'.cr.fits'
    maskname = basename+'.mask.fits'
    if not fi.check_version(inhdl):
        inhdl.close()
        return crname, maskname, False
    inhdl.close()

    if os.path.isfile(crname):
        if not overwrite:
            print('\t Cosmicray-removed frame already exits. ' + crname)
            print('\t This procedure is skipped.')
            inhdl.close()
            return crname, maskname, True
    
    print('Cosmicray removing for ' + str(inhdr['FRAMEID']))

    nx = scidata.shape[1]
    ny = scidata.shape[0]

    # Cosmicray removing
    print('\t L.A.Cosmic')
    #fitdata = scidata - residualdata
    crmask, cleandata = \
        astroscrappy.detect_cosmics(scidata, sigclip=sigclip, sigfrac=sigfrac, \
                objlim=objlim, gain=1.0, readnoise=4.0, satlevel=np.inf, \
                pssl=0.0, niter=niter, sepmed=False, cleantype='medmask', \
                fsmode='median', verbose=True)

    # Writing output files
    cleanhdu = fits.PrimaryHDU(data=cleandata)
    #cleanhdu = fits.PrimaryHDU(data=cleandata)
    cleanhdl = fits.HDUList([cleanhdu])
    cleanhdl[0].header = inhdr
    cleanhdl[0].header['LACO_VER'] = (astroscrappy.__version__, \
                                      'Python script version of LACOSMIC') 
    
    crmaskint = crmask.astype(np.uint8)
    maskhdu = fits.PrimaryHDU(data=crmaskint)
    #maskhdu = fits.PrimaryHDU(data=fitdata)
    maskhdl = fits.HDUList([maskhdu])
    maskhdl[0].header = inhdr
    maskhdl[0].header['LACO_VER'] = (astroscrappy.__version__, \
                                      'Python script version of LACOSMIC') 

    cleanhdl.writeto(crname, overwrite=overwrite)
    maskhdl.writeto(maskname, overwrite=overwrite)

    cleanhdl.close()
    maskhdl.close()

    print('\t Cleaned image '+crname)
    print('\t Mask image: '+maskname)
    return crname, maskname, True


if __name__ == '__main__':
    # Analize argments
    parser=argparse.ArgumentParser(description='This is the script '+\
                                   'for cosmicray removing using LACOS.')
    parser.add_argument('-o', help='Overwrite flag', dest='overwrite', \
                        action='store_true',default=False)
    parser.add_argument('infile', help='Input file name')
    parser.add_argument('-sigclip', help='Laplacian-to-noise limit for '+\
            'cosmic ray detection.  (default: 5.0)', default=5.0, type=float)
    parser.add_argument('-sigfrac',help='Fractional detection limit for '+\
            'neighboring pixels. (default: 0.4)', default=0.4, type=float)
    parser.add_argument('-niter',help='Number of iterations of the L.A.'+\
            'Cosmic algorithm to perform. (default: 4)', default=4, type=int)
    args = parser.parse_args()

    cosmicrays(args.infile, sigclip=args.sigclip, sigfrac=args.sigfrac, \
               niter=args.niter, overwrite=args.overwrite)
