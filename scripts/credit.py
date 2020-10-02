#!/usr/bin/env python

import os
import shutil
import numpy as np
import argparse
from astropy.io import fits
from pyraf import iraf


def credit(frameid):
    if os.path.exists(frameid+'.cr_org.fits'):
        print(frameid+'.cr_org.fits exists. '+
              'No need to backup the original file.')
    else:
        print('Copying ' + frameid + '.cr.fits to ' +
              frameid + '.cr_org.fits')
        shutil.copy(frameid+'.cr.fits', frameid+'.cr_org.fits')
    if os.path.exists(frameid+'.mask_org.fits'):
        print(frameid+'.mask_org.fits exists. ' + 
              'No need to backup the original file.')
    else:
        print('Copying ' + frameid + '.mask.fits to ' +
              frameid + '.mask_org.fits')
        shutil.copy(frameid+'.mask.fits', frameid+'.mask_org.fits')
    
    iraf.set(stdimage='imt8192')
    iraf.imedit(frameid+'.cr.fits',
        command='display $image 1 erase=$erase fill=no order=0 >& dev$null')

    data_ov = fits.getdata(frameid+'.ov.fits')
    data_cr = fits.getdata(frameid+'.cr.fits')
    hdl_mask = fits.open(frameid+'.mask.fits', mode='update')
    data_temp = data_ov - data_cr
    np.seterr(invalid='ignore')  # ignore RuntimeWarning in dividing 0 by 0.
    hdl_mask[0].data = np.nan_to_num(data_temp / data_temp)
    hdl_mask.close()
    return
        
if __name__ == '__main__':
    parser=argparse.ArgumentParser(
        description='This is the script for editing residuals in ' + 
                    'cosmic ray removing.')
    parser.add_argument('frameid', help='Frame ID.')
    args = parser.parse_args()

    credit(args.frameid)
