#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import argparse
from astropy.io import fits

def crresiduals(frameid):
    data_cr = fits.getdata(frameid+'.cr.fits')
    data_ov = fits.getdata(frameid+'.ov.fits')
    data_mask = fits.getdata(frameid+'.mask.fits')

    readnoise = 4.0
    nsig = 3.5

    reslist = []
    reslist2 = []
    for x in range(data_mask.shape[1]):
        for y in range(data_mask.shape[0]):
            if data_mask[y,x] == 1:
                ave = np.average(data_cr[y-1, x-2:x+3])
                msig = np.std(data_cr[y-1, x-2:x+3])
                tsig = np.sqrt(ave + readnoise**2)
                if ave > readnoise * 4:
                    if data_cr[y-1,x] > ave + nsig * tsig:
                        if msig < tsig * 3:
                            reslist.append([x, y-1, data_cr[y-1,x], ave, tsig, msig])
                        else:
                            reslist2.append([x, y-1, data_cr[y-1,x], ave, tsig, msig])
    reslistnp = np.array(reslist)
    reslistnp2 = np.array(reslist2)

    np.savetxt('reslist.dat',reslistnp, fmt='%5d %5d %.2f %.2f %.2f %.2f')
    np.savetxt('reslist2.dat',reslistnp2, fmt='%5d %5d %.2f %.2f %.2f %.2f')
    plt.imshow(np.log10(data_ov))
    plt.scatter(reslistnp[:,0], reslistnp[:,1])
    plt.scatter(reslistnp2[:,0], reslistnp2[:,1])
    plt.show()
    
    return

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='This is the '+\
            'script for checking cosmic ray removing.')
    parser.add_argument('frameid', help='Frame ID')
    args = parser.parse_args()

    crresiduals(args.frameid)
    
