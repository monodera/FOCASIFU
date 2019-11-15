#!/usr/bin/env python
# python3 OK

import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from numpy.polynomial.chebyshev import chebval
import focasifu as fi
import os
from astropy.io import fits
import re

def fit_gap_coordinate(infile, overwrite=False):
    # Retern is the hdl for a databe with the extracted 12 spectra.
    #
    print('\n#############################')
    print('Fitting the spectrum gap coordinates.')

    gapcoef_file = os.path.splitext(infile)[0]+'.gapcoef'
    if os.path.exists(gapcoef_file):
        if overwrite:
            os.remove(gapcoef_file)
        else:
            print('\t Coefficiet file already exists: ' + gapcoef_file)
            print('\t This precedure is skipped.')
            return gapcoef_file

    # Reading the id-file created by Identify and Reidentify tasks.
    f = open('database/id'+os.path.splitext(infile)[0],'r')
    lines = f.readlines()
    f.close()

    # Counting the number of data
    maxdatanum = 0
    for line in lines:
        if line.find('image') >= 0:
            maxdatanum = maxdatanum + 1

    # Reading the coordinate list file
    binfct1 = fits.getval(infile, 'BIN-FCT1')
    coordlistfile = fi.filibdir+'pseudoslitgap_binx'+str(binfct1)+'.dat'
    coordlist = np.genfromtxt(coordlistfile, dtype=['f','U8'])
    
    # Creating the array of the pseudo-slit-gap coordinates
    x = np.zeros(maxdatanum)
    y = np.zeros((len(coordlist),maxdatanum))
    linenum = 0
    datanum = -1
    l=0
    while l < len(lines):
        items = lines[l].split()
        if len(items) > 0:
            if items[0] == 'image':
                a = re.split('[,\]]',lines[l])
                datanum = datanum + 1
                x[datanum] = int(a[1])
            if items[0] =='features':
                featurenum = int(items[1])
                for i in range(featurenum):
                    l=l+1
                    items = lines[l].split()
                    for j in range(len(coordlist)):
                        if np.float32(items[2]) == coordlist[j][0]:
                            y[j,datanum] = np.float32(items[0])

        l=l+1

    # Fitting the pseudo-slit-gap coordinates
    order = 2
    coef = np.zeros((len(coordlist),order+1))
    weight0 = np.ones((len(coordlist), maxdatanum), dtype=np.int)
    weight = np.ones((len(coordlist), maxdatanum), dtype=np.int)
    markersize = 10
    
    for k in range(len(coordlist)):
        for i in range(maxdatanum):
            if y[k,i] == 0.0:
                weight0[k,i] = 0.0

        coef[k,:], weight[k,:], stat = fi.cheb1Dfit(x, y[k,:], order=order, \
                                    weight=weight0[k,:], niteration=3, \
                                    high_nsig=3., low_nsig=3.)
        if not stat:
            print('Warrning at k='+str(k)+'in fitting')

    # Plotting the pseudo-slit-gap coordinates and the fitting results
    cmap = plt.get_cmap("hsv")
    plt.figure(figsize=(14,5))
    plt.subplot(1,2,1)
    imdata = fits.getdata(os.path.splitext(infile)[0]+'.fits')
    immax = np.max(imdata)
    ploty = np.array(range(imdata.shape[0]))
    plt.imshow(imdata, origin='lower',aspect='auto', \
               norm=LogNorm(vmin=1, vmax=immax))
    for i in range(len(coordlist)):
        x_temp_accept, x_temp_reject = fi.datafiltering(x, weight0[i,:])
        y_temp_accept, y_temp_reject = fi.datafiltering(y[i], weight0[i,:])
        weight_temp_accept, weight_temp_rejected = \
                            fi.datafiltering(weight[i,:], weight0[i,:])

        x_accept, x_reject = fi.datafiltering(x_temp_accept, weight_temp_accept)
        y_accept, y_reject = fi.datafiltering(y_temp_accept, weight_temp_accept)

        plt.scatter(y_accept-1, x_accept-1, marker='o', \
                    c=cmap(float(i)/len(coordlist)), s=markersize)
        plt.scatter(y_reject-1, x_reject-1, marker='x', \
                    c=cmap(float(i)/len(coordlist)), s=markersize)
        plt.plot(chebval(ploty-1, coef[i,:])-1, ploty, \
                    c=cmap(float(i)/len(coordlist)))

    plt.title('Identified positions')
    plt.ylabel('Y (pix)')
    plt.xlabel('X (pix)')

    plt.subplot(1,2,2)
    plt.subplots_adjust(left = 0.1, right = 0.85)
    plt.title('Fit residual')
    plt.xlabel('Y (pix)')
    plt.ylabel('Fit residual (pix)')
    for i in range(len(coordlist)):
        x_temp_accept, x_temp_reject = fi.datafiltering(x, weight0[i,:])
        y_temp_accept, y_temp_reject = fi.datafiltering(y[i], weight0[i,:])
        weight_temp_accept, weight_temp_rejected = \
                        fi.datafiltering(weight[i,:], weight0[i,:])

        x_accept, x_reject = fi.datafiltering(x_temp_accept, weight_temp_accept)
        y_accept, y_reject = fi.datafiltering(y_temp_accept, weight_temp_accept)
        yfit_accept = chebval(x_accept, coef[i,:])
        yfit_reject = chebval(x_reject, coef[i,:])
        color = cmap(float(i)/len(coordlist))
        plt.scatter(x_accept-1, y_accept - yfit_accept, marker='o', \
                    c=color, s=markersize, label=coordlist[i][1])
        plt.scatter(x_reject-1, y_reject - yfit_reject, marker='x', \
                    c=color, s=markersize)

    plt.legend(bbox_to_anchor=(1.1,1.1),loc='upper left', borderaxespad=0.)
    plt.grid()
    # Followings are for avoiding the conflict between matplotlib and pyraf.
    plt.draw()
    try:
        plt.pause(-1)
    except:
        pass

    np.savetxt(gapcoef_file, coef)
    return gapcoef_file

if __name__ == '__main__':
    # Analize argments
    parser=argparse.ArgumentParser(description='This is the script'+ \
                                   'for fitting spectrum edge coordinates.')
    parser.add_argument('infile', help='Combined CAL flat image')
    parser.add_argument('-o', help='Overwrite flag', dest='overwrite', \
                        action='store_true',default=False)
    args = parser.parse_args()

    fit_gap_coordinate(args.infile, overwrite=args.overwrite)

