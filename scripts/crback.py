#!/usr/bin/env python

import os
import shutil
import numpy as np
import argparse
from astropy.io import fits


def crback(frameid, coordtable):
    data_ov = fits.getdata(frameid+'.ov.fits')

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
    
    hdl_cr = fits.open(frameid+'.cr.fits', mode='update')
    data_cr = hdl_cr[0].data
    
    hdl_mask = fits.open(frameid+'.mask.fits', mode='update')
    data_mask = hdl_mask[0].data

    coords = np.loadtxt(coordtable, dtype='int')

    if coords.ndim == 1:
        coord_num = 1
    elif coords.ndim == 2:
        coord_num = coords.shape[0]
    else:
        print('Error in the coodinate list file')
        return

    print('Number of coordinates: '+str(coord_num))

    if coords.ndim == 1:
        print(coords[1]-1, coords[0]-1)
        data_cr[coords[1]-1, coords[0]-1] = data_ov[coords[1]-1, coords[0]-1]
        data_mask[coords[1]-1, coords[0]-1] = 0
    elif coords.ndim == 2:
        for i in range(coord_num):
            print(coords[i,1]-1, coords[i,0]-1)
            data_cr[coords[i,1]-1, coords[i,0]-1] = data_ov[coords[i,1]-1, coords[i,0]-1]
            data_mask[coords[i,1]-1, coords[i,0]-1] = 0

    hdl_cr.close()
    hdl_mask.close()

    return
        
if __name__ == '__main__':
    parser=argparse.ArgumentParser(
        description='This is the script for replacing the pixel'+
        ' value to the value before cosmicray removing.')
    parser.add_argument('frameid', help='Frame ID.')
    parser.add_argument('coordtable',
                        help='List file of pixel coordinates to be replaced.')
    args = parser.parse_args()

    crback(args.frameid, args.coordtable)
