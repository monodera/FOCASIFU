#!/usr/bin/env python

import argparse
import sys
import focasifu as fi
from astropy.io import fits
import numpy as np
from numpy.polynomial.chebyshev import chebval

def extract(inhdl, gapcoef_file):
    #print('\n#############################')
    #print('Extracting spectra.')
    indata = inhdl[0].data
    binfct1 = inhdl[0].header['BIN-FCT1']

    # Preparing the output initialize data.
    cubedata = np.zeros((24,indata.shape[0],int(200/binfct1)), dtype=np.float32)
    
    # Extracting the spectra for each pseudo-slit and replacing
    # the values for neighboring spectra to zero.
    coef = np.loadtxt(gapcoef_file)
    y = np.array(range(1,indata.shape[0]+1))
    margin = int(10/binfct1)

    ## For ch01
    xfit2 = chebval(y, coef[0,:])
    xstart = int(np.min(xfit2)) - margin
    if xstart + cubedata.shape[2] > indata.shape[1]:
        xend = indata.shape[1]
    else:
        xend = xstart + cubedata.shape[2] - 1

    cubedata[0, :, :xend-xstart+1] = indata[:, xstart-1:xend]
    for j in range(xfit2.size):
        cubedata[0, j, 0:int(xfit2[j])-xstart+1] = 0.0

    ## For ch02-11
    for i in range(1,11): # i is (Ch number -1)
        xfit1 = xfit2
        xfit2 = chebval(y, coef[i,:])
        xstart = int(np.min(xfit2))-margin
        #xend   = int(np.max(xfit1))+margin
        xend = xstart + cubedata.shape[2] - 1
        #cubedata[i, :, :xend-xstart+1] = indata[:, xstart:xend+1]
        cubedata[i, :, :] = indata[:, xstart-1:xend]
        for j in range(xfit2.size):
            cubedata[i, j, 0:int(xfit2[j])-xstart+1] = 0.0
            cubedata[i, j, int(xfit1[j])-xstart+2:] = 0.0

    ## For ch12
    #xend = int(np.max(xfit2))+margin
    xstart = int(np.min(xfit2))-int(138/binfct1)-margin
    xend = xstart+cubedata.shape[2]-1
    #cubedata[11,:,:xend-xstart+1] = indata[:,xstart:xend+1]
    cubedata[11, :, :] = indata[:, xstart-1:xend]
    for j in range(xfit2.size):
        cubedata[11, j, int(xfit2[j])-xstart+2:] = 0.0

    ## For ch13
    xfit2 = chebval(y, coef[11,:])
    xstart = int(np.min(xfit2)) - margin
    xend = xstart+cubedata.shape[2] -1
    #cubedata[12,:,:xend-xstart] = indata[:,xstart:xend]
    cubedata[12, :, :] = indata[:, xstart-1:xend]
    for j in range(xfit2.size):
        cubedata[12,j,0:int(xfit2[j])-xstart+1] = 0.0

   ## For ch14-22
    for i in range(13,22): # i is (Ch number -1)
        xfit1 = xfit2
        xfit2 = chebval(y, coef[i-1,:])
        xstart = int(np.min(xfit2)) - margin
        #xend   = int(np.max(xfit1)) + margin
        xend = xstart+cubedata.shape[2] -1
        #cubedata[i,:,:xend-xstart+1] = indata[:,xstart:xend+1]
        cubedata[i, :, :] = indata[:, xstart-1:xend]
        for j in range(xfit2.size):
            cubedata[i,j,0:int(xfit2[j])-xstart+1] = 0.0
            cubedata[i,j,int(xfit1[j])-xstart+2:] = 0.0

    ## For ch23
    xstart23 = int(xstart - 133.0/binfct1) - margin
    #xend23 = int(np.max(xfit2)) + margin
    xend23 = xstart23+cubedata.shape[2] -1
    #cubedata[22, :, :xend23-xstart23] = indata[:,xstart23:xend23]
    cubedata[22, :, :] = indata[:, xstart23-1:xend23]
    for j in range(xfit2.size):
        cubedata[22, j, int(xfit2[j])-xstart23+2:] = 0.0
                 
    ## For sky spectrum
    xstart24 = int(xstart - 360.0/binfct1)
    #xend24 = int(xend - 360.0/binfct1) + margin
    xend24 = xstart24+cubedata.shape[2] -1
    #cubedata[23,:,:xend24-xstart24] = indata[:,xstart24:xend24]
    cubedata[23, :, :] = indata[:, xstart24-1:xend24]
    
    # Creating the output hdl
    outhdu = fits.PrimaryHDU(data=cubedata)
    outhdl = fits.HDUList([outhdu])
    outhdl[0].header = inhdl[0].header
    outhdl[0].header['GAPCOEFF']=(gapcoef_file, 'Coefficient file used for extraction')

    inhdl.close()
    
    return outhdl

def writetochimages(cubehdl, basename, overwrite=False):
    
    basename = cubehdl[0].header['FRAMEID']

    for i in range(0,24):
        outdata = cubehdl[0].data[i,:,:]
        outhdu = fits.PrimaryHDU(data=outdata)
        outhdl = fits.HDUList([outhdu])
        outhdl[0].header = cubehdl[0].header
        
        outfitsname = fi.chimagedir + basename+'.ch%02d.fits'%(i+1)
        outhdl.writeto(outfitsname)
        outhdl.close()
        print('\t '+outfitsname)

    return

if __name__ == '__main__':
    # Analize argments
    parser=argparse.ArgumentParser(description='This is the script for fitting spectrum edge coordinates.')
    parser.add_argument('infile', help='Image to be extracted.')
    parser.add_argument('gapcoef_file', help='Coeficient file for gap position function.')
    parser.add_argument('-o', help='Overwrite flag', dest='overwrite', action='store_true',default=False)
    args = parser.parse_args()

    hdl = fits.open(args.infile)
    cubehdl = extract(hdl, args.gapcoef_file)
    basename = cubehdl[0].header['FRAMEID']
    writetochimages(cubehdl, basename, overwrite=args.overwrite)
