#!/usr/bin/env python
# python3 OK

import os
import focasifu as fi
import argparse
import numpy as np
import math
from astropy.io import fits
from scipy.ndimage.interpolation import shift as imshift
import matplotlib.pyplot as plt


def flatfielding(infile, domeflat, calflat, domecomp=None, comp=None, overwrite=False):
    print('\n#############################')
    print('Flat fielding.')
   
    inhdl = fits.open(infile)
    inhdr = inhdl[0].header
    el = inhdr['ALTITUDE']
    insrot = inhdr['INSROT']
    binfac1 = inhdr['BIN-FCT1'] # X direction on DS9
    binfac2 = inhdr['BIN-FCT2'] # Y direction on DS9
    basename = inhdr['FRAMEID']
    ffname = basename+'.ff.fits'
    if not fi.check_version(inhdl):
        return ffname, False

    if os.path.isfile(ffname):
        if not overwrite:
            print('\t Flatfielded frame already exits. ' + ffname)
            print('\t This procedure is skipped.')
            inhdl.close()
            return ffname, True
    
    highflat = domeflat+'.fcmb_high.fits'
    highhdl = fits.open(highflat)
    if not fi.check_version(highhdl):
        return ffname, False
    
    lowflat = domeflat+'.fcmb_low.fits'
    lowhdl = fits.open(lowflat)
    if not fi.check_version(lowhdl):
        return ffname, False

    print('\t High frequency flat frame: '+highflat)
    print('\t Low frequency flat frame:  '+lowflat)

    # Getting X shift
    caldata = fits.getdata(calflat+'.fcmb.fits')
    domedata = fits.getdata(domeflat+'.fcmb.fits')
    y1 = int(caldata.shape[0]/2.)
    y2 = y1+10
    x1 = int(2070/binfac1)
    x2 = int(3890/binfac1)
    dome1d = np.mean(domedata[y1:y2,x1:x2], axis=0)
    cal1d = np.mean(caldata[y1:y2,x1:x2], axis=0)
    dx = fi.cross_correlate(cal1d, dome1d, sep=0.01, fit=True, niteration=3, \
                            high_nsig=1.0, low_nsig=1.0)

    # Getting Y shift
    dy=0.0
    if domecomp != None:
        x1_2 = int(1100*2/binfac1)
        comp_data = fits.getdata(comp+'.ov.fits')
        domecomp_data = fits.getdata(domecomp+'.ov.fits')
        comp1d = np.mean(comp_data[:,x1_2:x1_2+10], axis=1)
        domecomp1d = np.mean(domecomp_data[:,x1_2-int(dx+0.5):x1_2+10-int(dx+0.5)], axis=1)
        dy = fi.cross_correlate(comp1d, domecomp1d, sep=0.1, fit=False)
    
    print('\t Low freqency flat is shifted: dX=' + str(dx)[:5] + ' dY=' + str(dy)[:5])
    
    # Shifting the low frequency flat image
    shiftedlowdata = imshift(lowhdl[0].data, (dy,dx), order=5, mode='nearest')
    shiftedlow1d = np.mean(shiftedlowdata[y1:y2,x1:x2], axis=0)
    plt.plot(cal1d/np.mean(cal1d),label='CAL flat at object direction')
    plt.plot(dome1d/np.mean(dome1d),label='Dome flat before shift')
    plt.plot(shiftedlow1d/np.mean(shiftedlow1d),label='Dome flat after shift')
    plt.title('X shift check')
    plt.xlabel('X')
    plt.ylabel('Normarised count')
    plt.legend()
    plt.grid()
    plt.show()

    
    if domecomp != None:
        shifteddomecompdata = imshift(domecomp_data[:,x1_2-50:x1_2+60], (dy,dx), order=5, mode='nearest')
        shifteddomecomp1d = np.mean(shifteddomecompdata[:,50:60], axis=1)
        plt.plot(comp1d,label='Comparison at object direction')
        plt.plot(domecomp1d,label='Comparison before shift')
        plt.plot(shifteddomecomp1d,label='Comparison after shift')
        plt.title('Y shift check')
        plt.xlabel('Y')
        plt.ylabel('Count')
        plt.legend()
        plt.grid()
        plt.show()

    # Dividing the input image with the shifted low frequency flat image
    tempdata = inhdl[0].data / shiftedlowdata

    # Dividing with the high frequency flat image
    # Each image region is divided one by one not to be divided by 0
    # because CCD gap regions has 0 in FITS data. 
    outdata = np.zeros(tempdata.shape, dtype=np.float32)
    gap_x1 = inhdr['GAP_X1']
    gap_x2 = inhdr['GAP_X2']
    outdata[:, :gap_x1-1] = tempdata[:, :gap_x1-1] / \
                                      highhdl[0].data[:, :gap_x1-1]
    outdata[:, gap_x2:] = tempdata[:, gap_x2:] / \
                                    highhdl[0].data[:, gap_x2:]
    #outdata = tempdata / highhdl[0].data

    # Creating HDU data
    outhdu = fits.PrimaryHDU(data=outdata)
    outhdl = fits.HDUList([outhdu])
    outhdl[0].header = inhdr
    outhdl[0].header['FLATFILE']=(domeflat,'Frame ID used for flat fielding.')
    outhdl[0].header['FLATSFT1']=(dx, 'X shifted value for domeflat frame.')
    outhdl[0].header['FLATSFT2']=(dy, 'Y shifted value for domeflat frame.')
    outhdl.writeto(ffname, overwrite=overwrite)

    inhdl.close()
    lowhdl.close()
    highhdl.close()
    outhdl.close()
    print('\t Created flat fielded file: '+ffname)
    return ffname, True

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='This is the script for flat-fielding.')
    parser.add_argument('infile', help='Input FITS file')
    parser.add_argument('dflat', help='Dome flat frame ID')
    parser.add_argument('cflat', help='Cal flat frame ID')
    parser.add_argument('comp', help='Comarison frame ID for object')
    parser.add_argument('domecomp', help='Comparison frame ID for dome flat')
    parser.add_argument('-o', help='Overwrite flag', dest='overwrite', action='store_true',default=False)
    args = parser.parse_args()

    flatfielding(args.infile, args.dflat, args.cflat, args.comp, args.domecomp, overwrite=args.overwrite)
