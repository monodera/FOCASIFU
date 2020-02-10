#!/usr/bin/env python
# python3 OK

import sys
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.modeling.models import Gaussian2D
from astropy.modeling.fitting import LevMarLSQFitter
from photutils import aperture_photometry, EllipticalAperture
from photutils.centroids import centroid_com


def cutout(data, center, w=10):
    x1 = int(center[0]+0.5)-w
    x2 = int(center[0]+0.5)+w
    y1 = int(center[1]+0.5)-w
    y2 = int(center[1]+0.5)+w

    if x1 < 0:
        x1 = 0
    if x2 > data.shape[1]-1:
        x2 = data.shape[1]-1
    if y1 < 0:
        y1 = 0
    if y2 > data.shape[0]-1:
        y2 = data.shape[0]-1

    cutdata= data[y1:y2, x1:x2]
    initp = np.array((x1,y1))
    return cutdata, initp


def std1dspec(infile, startz=2000, nsigma=5, overwrite=False):
    print('\n#############################')
    print('Making 1D spectrum')
                              
    hdl = fits.open(infile)
    hdr = hdl[0].header
    
    scidata = hdl[0].data
    binfac1 = hdr['BIN-FCT1']

    # Showing the image 
    aspect = 0.43/(0.104*binfac1)
    fig=plt.figure()
    plt.title('Click on the star. ')
    plt.imshow(scidata[startz,:,:], aspect=aspect, \
               interpolation='nearest', origin='lower')

    global xc,yc
    xc = 0.0
    yc = 0.0

    def star_center(event):
        global xc,yc
        xc= event.xdata
        yc = event.ydata
        plt.close()
        return

    
    cid = fig.canvas.mpl_connect('button_press_event', star_center)
    print('\n\t Click near the star center.')
    plt.show()

    print('\t Initial star location: (%.2f, %.2f)'%(xc,yc))
    initc = np.array((xc,yc))
    cutdata, initp = cutout(scidata[startz,:,:], initc ,w=10)
    g_init = Gaussian2D(amplitude=np.max(cutdata),
                         x_mean=initc[0]-initp[0],
                         y_mean=initc[1]-initp[1],
                         x_stddev=2.0,
                         y_stddev=1.0,
                         theta=3.1416/2)
    g_init.theta.fixed = True
    fitter = LevMarLSQFitter()
    y, x = np.indices(cutdata.shape)
    gfit = fitter(g_init, x, y, cutdata)
    print('\t Initial 2D Gaussian fitting result:')
    print(gfit)
    position0 = np.array([gfit.x_mean.value, gfit.y_mean.value])
    position0 = position0 + initp
    position = position0

    a = gfit.x_stddev.value * nsigma
    b = gfit.y_stddev.value * nsigma
    theta = gfit.theta.value

    plt.imshow(scidata[startz,:,:], aspect=aspect, \
               interpolation='nearest', origin='lower')
    apertures = EllipticalAperture(position, a=a ,b=b,theta=theta)
    apertures.plot()
    print('\n\t Check the aperture, and close the plot window.')
    plt.title('Check the aperture')
    plt.show()

    global coords, ii, std1ddata, lam

    std1ddata = np.zeros(scidata.shape[0], dtype=np.float32)
    positions = np.zeros((scidata.shape[0], 2), dtype=np.float)

    # Aperture photometry with incleasing wavelength pix from startz 
    for i in range(startz,scidata.shape[0]):
        cutdata, initp = cutout(scidata[i,:,:],position)
        if np.min(cutdata) == np.max(cutdata):
            print('\t Cutdata is empty at '+str(i)+' pix.')
            break
        position_pre = position
        position = centroid_com(cutdata)
        position = position + initp
        if np.linalg.norm(position-position_pre) > 2.:
            print('\t Cetroid is not good at '+str(i)+' pix.')
            break
        positions[i,:] = position
        #apertures = EllipticalAperture(position, a=a ,b=b,theta=theta)
        #phot_table = aperture_photometry(scidata[i,:,:], apertures)   
        #std1ddata[i] = phot_table['aperture_sum'].data[0]

    # Aperture photometry with decreasing wavelength pix from startz 
    position = position0
    for i in range(startz-1,0,-1):
        cutdata, initp = cutout(scidata[i,:,:],position)
        if np.min(cutdata) == np.max(cutdata):
            print('\t Cutdata is empty! at ' + str(i) + ' pix.')
            break
        position_pre = position
        position = centroid_com(cutdata)
        position = position + initp
        if np.linalg.norm(position-position_pre) > 2.:
            print('\t Cetroid is not good at ' + str(i) + ' pix.')
            break
        positions[i,:] = position
        #apertures = EllipticalAperture(position, a=a ,b=b,theta=theta)
        #phot_table = aperture_photometry(scidata[i,:,:], apertures)   
        #std1ddata[i] = phot_table['aperture_sum'].data[0]


    # Plotting the 1D data & selecting the spectral range.
    crpix = hdr['CRPIX3']
    crval = hdr['CRVAL3']
    #cdelt = hdr['CDELT3']
    cdelt = hdr['CD3_3']
    object_name = hdr['OBJECT']

    npix = len(std1ddata)
    start = crval - (crpix-1)*cdelt
    stop = crval + (npix - crpix + 0.5)*cdelt
    lam = np.arange(start ,stop, cdelt)
    
    plt.plot(lam,positions[:,0])
    plt.title(object_name)
    plt.xlabel('Lambda (Angstrom)')
    plt.ylabel('X (pix)')
    plt.grid()
    plt.show()

    plt.plot(lam,positions[:,1])
    plt.title(object_name)
    plt.xlabel('Lambda (Angstrom)')
    plt.ylabel('Y (pix)')
    plt.grid()
    plt.show()
    
    return


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='This is the '+\
            'script for making a 1D spectrum of the standard star.')
    parser.add_argument('-o', help='Overwrite flag', dest='overwrite',\
            action='store_true',default=False)
    parser.add_argument('infile', help='Input FITS file.')
    parser.add_argument('-startz', help='Start Z pixel for aperture '+\
                        'photometry. (default: 2000)', default=2000, \
                        type=int)
    parser.add_argument('-nsigma', help='Number of sigmas for the '+\
                        'aperture size. (default: 5)', default=5, type=int)
    args = parser.parse_args()

    std1dspec(args.infile, startz=args.startz, nsigma=args.nsigma, \
                overwrite=args.overwrite)
