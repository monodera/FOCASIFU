#!/usr/bin/env python3
# python3 OK

from astropy.io import fits
import numpy as np
import os
import argparse
import focasifu as fi
import sys
from multiprocessing import Pool, cpu_count, current_process
import time


def correlate_each(args):
    data = args[0]
    sky1d = args[1]
    chstart = args[2]
    chend = args[3]
    
    dy = np.zeros(data.shape[1:3], dtype=np.float32)
    for i in range(chstart, chend+1):
        if current_process().name == 'ForkPoolWorker-1':
            sys.stdout.write('\r\t\t {:.1f}% done'
                        .format(float(i-chstart)/float(chend - chstart + 1)*100.))
            sys.stdout.flush()            
        for j in range(data.shape[2]):
            dy[i,j] = fi.cross_correlate(data[:,i,j], sky1d,
                                     sep=0.01, kind='cubic')
    sys.stdout.write('\r\t\t 100.0% done')
    sys.stdout.flush()
    return dy


def multi_process_correlate(data, ref1d):
    print('\t Correlating')

    # Getting the number of CPU cores
    cpunum = cpu_count()
    print('\t\t Number of CPU: {}'.format(cpunum))

    # Making parameters
    chstep = int(data.shape[1]/cpunum)
    params = []
    for i in range(cpunum-1):
        params.append([data, ref1d, i*chstep, (i+1)*chstep-1])
    params.append([data, ref1d, chstep*(cpunum-1), data.shape[1]-1])

    # Multiprocessing
    p = Pool(cpunum)
    start = time.time()
    results = p.map(correlate_each, params)
    elapsed_time = time.time() - start
    print('\n\t\t Elapsed time: {:.1f} sec'.format(elapsed_time))

    # Merging data
    results_np = np.array(results)
    dy = np.zeros(data.shape[1:3], dtype=np.float32)
    for i in range(results_np.shape[0]):
        dy = dy + results_np[i]

    return dy


def get_sky_shift(comp, x1=53, x2=62, overwrite=False):
    print('\n#############################')
    print('Sky subtraction')
    hdl = fits.open(comp+'.xyl.fits')
    comp_data = hdl[0].data
    basename = hdl[0].header['FRAMEID']
    outfile = basename + '.sky_shift.dat'
    
    if not fi.check_version(hdl):
        return outfile, False
    
    if os.path.isfile(outfile):
        if not overwrite:
            print('\t Sky shift data file already exits. '+outfile)
            print('\t This procedure is skipped.')
            return outfile, True
        
    # Making 1D sky spectrum of the comparison data.
    comp_sky1d = np.mean(comp_data[:,23,x1-1:x2],axis=1)

    # Deriving shifts of the sky spectrum
    dy = multi_process_correlate(comp_data, comp_sky1d)
    np.savetxt(outfile, dy, fmt='%.2f')

    return outfile, True
    
if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='This is the '+\
            'script for deriving deviations between object spectra ' + \
                                   'and sky one.')
    parser.add_argument('-o', help='Overwrite flag', dest='overwrite',\
            action='store_true',default=False)
    parser.add_argument('comp', help='Comparison ID')
    parser.add_argument('-x1', help='Start pixel for integrating '+\
            'the sky spectrum. (default: 53)', default=53, type=int)
    parser.add_argument('-x2', help='End pixel for integrating '+\
            'the sky spectrum. (default: 62)', default=62, type=int)
    args = parser.parse_args()

    get_sky_shift(args.comp, x1=args.x1, x2=args.x2, \
           overwrite=args.overwrite)
