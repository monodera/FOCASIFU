#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import argparse
from astropy.io import fits

def crplot(image1, image2, x):
    data1_ov = fits.getdata(image1+'.ov.fits')
    data1_cr = fits.getdata(image1+'.cr.fits')
    data1_mask = fits.getdata(image1+'.mask.fits')
    
    data2_ov = fits.getdata(image2+'.ov.fits')
    data2_cr = fits.getdata(image2+'.cr.fits')
    data2_mask = fits.getdata(image2+'.mask.fits')

    y = np.arange(1,data1_ov.shape[0]+1)

    while(1):
        plt.plot(y, data1_ov[:,x-1], label=image1+'.ov')
        plt.plot(y, data1_cr[:,x-1], label=image1+'.cr')
    
        plt.plot(y, data2_ov[:,x-1], label=image2+'.ov')
        plt.plot(y, data2_cr[:,x-1], label=image2+'.cr')

        plt.title('X='+str(x)+' in DS9')
        plt.xlabel('Y in DS9')
        plt.legend()
        plt.show()
        x=x+1

    
if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='This is the '+\
            'script for checking cosmic ray removing.')
    parser.add_argument('frame1', help='Frame ID 1')
    parser.add_argument('frame2', help='Frame ID 2')
    parser.add_argument('x', help='X coordinate to be plotted.', type=int)
    args = parser.parse_args()

    crplot(args.frame1, args.frame2, args.x)
    
