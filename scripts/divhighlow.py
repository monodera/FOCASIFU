#!/usr/bin/env python

import sys
import os
import time
import argparse
import numpy as np
from numpy.polynomial.chebyshev import chebval
from multiprocessing import Pool, cpu_count, current_process
from astropy.io import fits
import copy
import focasifu as fi

def fixbadcolumn(inhdl):
    # Bad pixel correction
    print('\t Temporarily correcting bad column.')

    # Checking the version consistency
    if not fi.check_version(inhdl):
        return inhdl, False

    scidata = copy.deepcopy(inhdl[0].data)
    # Bad pixel coordinates before removing overscan regions.
    # x1,x2,y1,y2 in DS9 corrdinate.
    badpix_dict = {'21':  # for 2x1 bin
                   [
                       [1445,1445,2336,4169],
                       [1334,1334,1,2194]
                   ],'22':  # for 2x2 bin Dummy
                   [
                       [397,397,1189,2105],
                       [397,397,1189,2105]
                   ],'11':  # for 1x1 bin
                   [
                       [2889,2889,2336,4169],
                       [2667,2669,1,2195]
                   ]
                   }

    binfct1 = inhdl[0].header['BIN-FCT1']
    binfct2 = inhdl[0].header['BIN-FCT2']
    badpix = np.array(badpix_dict[str(binfct1)+str(binfct2)])

    for i in range(badpix.shape[0]):
        x1 = badpix[i,0]
        x2 = badpix[i,1]
        y1 = badpix[i,2]
        y2 = badpix[i,3]
        xlen = x2 - x1 + 2
        for x in range(x1-1, x2):
            scidata[y1-1:y2, x] = scidata[y1-1:y2, x1-2] + \
                                  (scidata[y1-1:y2, x2] - \
                                   scidata[y1-1:y2,x1-2])/ xlen * (x-x1+2)

    
    # Creating the output hdl
    outhdu = fits.PrimaryHDU(data=scidata)
    outhdl = fits.HDUList([outhdu])
    outhdl[0].header = inhdl[0].header
    return outhdl, True


def fixbadpix(inhdl, maskfile=None):
    print('\t Temporarily correcting bad pixels')
    
    data = copy.deepcopy(inhdl[0].data)
    inhdr = inhdl[0].header
    binfct1 = inhdr['BIN-FCT1']
    binfct2 = inhdr['BIN-FCT2']
    if maskfile is None:
        maskfile =fi.filibdir+ \
                    'dustposition_%dx%dbin.fits'%(binfct1,binfct2)
    maskdata = fits.getdata(maskfile)
        
    # version check
    if not fi.put_version(inhdl):
        return inhdl, False

    for x in range(maskdata.shape[1]):
        for y in range(maskdata.shape[0]):
            if maskdata[y,x] == 1:
                ys = y
                while maskdata[y,x] == 1:
                    y = y+1
                ye = y
                for i in range(ys,ye):
                    data[i,x] = \
                        ((ye-i)*data[ys-1,x] + (i-ys+1)*data[ye,x]) / \
                        (ye-ys+1)
    
    # Creating the output hdl
    outhdu = fits.PrimaryHDU(data=data)
    outhdl = fits.HDUList([outhdu])
    outhdl[0].header = inhdl[0].header
    return outhdl, True


def colmun_fitting(scidata, xrange):
    stat = True
    x1 = xrange[0]
    x2 = xrange[1]
    tempdata = np.zeros(scidata.shape, dtype=np.float32)
    radius = 5
    for j in range(x1, x2):
        if current_process().name == 'ForkPoolWorker-1':
            if (j-x1)%5 == 4:
                sys.stdout.write('\r\t ' + str((j-x1)/(x2-x1)*100)[:4] +
                                 '% done')
                sys.stdout.flush()
                
        
        for i in range(radius, scidata.shape[0]-radius):
            x = np.array(range(i-radius, i+radius-1))
            coef, weight, stat  = fi.cheb1Dfit(x, scidata[i-radius:i+radius-1, j], \
                                order=3, niteration=1, high_nsig=2.0, \
                                low_nsig=2.0)
            if not stat:
                print('Warning at ('+str(j+1)+', '+str(i+1)+') in DS9.')
                print('Data: ',scidata[i-radius:i+radius-1, j])
                print('Weight: ',weight)
            
            tempdata[i, j] = chebval(i, coef)
        for i in range(radius):
            tempdata[i, j] = tempdata[radius, j]
        for i in range(scidata.shape[0]-radius, scidata.shape[0]):
            tempdata[i, j] = tempdata[scidata.shape[0]-radius-1, j] 
            
    return tempdata


def wrapper(args):
    return colmun_fitting(args[0], args[1])


def multi_process_fitting(scidata):
    print('\t Fitting')
    cpunum = cpu_count()
    print('\t Number of CPU: '+str(cpunum))
    p = Pool(cpunum)
    colnum = int(scidata.shape[1]/cpunum)
    xrange = []
    for i in range(cpunum-1):
        xrange.append([i*colnum, (i+1)*colnum])
    xrange.append([(cpunum-1)*colnum, scidata.shape[1]])
    params = [(scidata, i) for i in xrange]

    start = time.time()
    results = p.map(wrapper, params)
    elapsed_time = time.time() - start
    print ('\n\t Elapsed time: ' + str(elapsed_time)+' sec')
    results_np = np.array(results)
    data = np.zeros(scidata.shape, dtype=np.float32)
    for i in range(results_np.shape[0]):
        data = data + results_np[i,:,:]

    return data
    

def divhighlow(infile, maskfile=None, overwrite=False):
    print('\n#############################')
    print('Dividing the flat frame into the high and low frequency components')

    inhdl = fits.open(infile)
    inhdr = inhdl[0].header

    basename = inhdr['FRAMEID']
    lowfile = basename+'.fcmb_low.fits'
    highfile = basename+'.fcmb_high.fits'
        
    if os.path.isfile(lowfile):
        if not overwrite:
            print('\t Divided flat frame already exists. '+lowfile)
            print('\t This precedure is skipped.')
            return
            
    if os.path.isfile(highfile):
        if not overwrite:
            print('\t Divided flat frame already exists. '+highfile)
            print('\t This precedure is skipped.')
            return
        
    # Bad pixel treatment
    fixed_hdl,stat = fixbadcolumn(inhdl)
    if stat == False:
        inhdl.close()
        return

    fixed_hdl, stat = fixbadpix(fixed_hdl, maskfile=maskfile)
    if stat == False:
        inhdl.close()
        return
    
    fixed_data = fixed_hdl[0].data
    normval = fi.getmedian(fixed_data, lower=1000)
    inhdr['NORMVAL'] = (normval, 'Value used for flat normalization.')

    # Fitting for low frequency component
    lowdata = multi_process_fitting(fixed_data)

    lowdata_norm = lowdata / normval
    lowhdu = fits.PrimaryHDU(data=lowdata_norm)
    lowhdl = fits.HDUList([lowhdu])
    lowhdl[0].header = inhdr
    lowhdl.writeto(lowfile, overwrite=overwrite)
    lowhdl.close()

    # Getting high frequency image
    # Each image region is divided one by one not to be divided by 0
    # because CCD gap regions has 0 in FITS data.
    scidata = inhdl[0].data
    highdata = np.zeros(scidata.shape, dtype=np.float32)
    gap_x1 = inhdr['GAP_X1']
    gap_x2 = inhdr['GAP_X2']
    highdata[:, :gap_x1-1] = scidata[:, :gap_x1-1] / \
                                      lowdata[:, :gap_x1-1]
    highdata[:, gap_x2:] = scidata[:, gap_x2:] / \
                                    lowdata[:, gap_x2:]

    highhdu = fits.PrimaryHDU(data=highdata)
    highhdl = fits.HDUList([highhdu])
    highhdl[0].header = inhdl[0].header
    highhdl.writeto(highfile, overwrite=overwrite)
    highhdl.close()

    inhdl.close()    
    print('')
    print('\t Low frequency image: '+lowfile)
    print('\t High frequency image: '+highfile)
    print()
    
    return


if __name__ == '__main__':
    # Analize argments
    parser=argparse.ArgumentParser(description='This is the reduction script for an object frame.')
    parser.add_argument('domeflat', help='Combined domeflat frame')
    parser.add_argument('-mask', help='Mask file name', default=None)
    parser.add_argument('-o', help='Overwrite flag', dest='overwrite', action='store_true',default=False)
    args = parser.parse_args()

    divhighlow(args.domeflat, maskfile=args.mask, overwrite=args.overwrite)
