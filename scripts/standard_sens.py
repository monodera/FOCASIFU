#!/usr/bin/env python
# python3 OK

import sys
import os
import argparse
from astropy.io import fits
import focasifu as fi

# Not to display warning.
temp_stderr = sys.stderr
sys.stderr = open('/dev/null', 'w')
from pyraf import iraf
sys.stderr = temp_stderr  # Back to the stadard error output

    
def standard_sens(infile, caldir=')_.caldir', noext=False,
                  overwrite=False):
    print('\n#############################')
    print('Deriving sensitivity funciton')
    
    # Not to display items in IRAF packages
    sys.stdout = open('/dev/null', 'w')
    iraf.noao()
    iraf.onedspec()
    sys.stdout = sys.__stdout__ # Back to the stadard output

    basename = fits.getval(infile, 'FRAMEID')
    std = basename + '.std'

    if noext:
        extinction = ''
    else:
        extinction = fi.filibdir+'mkoextinct.dat'

    if os.path.isfile(std) and not overwrite:
        print('\t The output file of IRAF STANDARD '+\
              'task already exits. '+std)
        print('\t STANDARD is skipped.')
    else:
        if overwrite:
            print('Removing '+std)
            os.remove(std)
        
        iraf.standard(infile, std, extinction=extinction,\
                      caldir=caldir, beam_sw='no', aperture='')
        print('Output file of IRAF STANDARD task: '+std)

    sens = basename + '.sens.fits'
    if os.path.isfile(sens) and not overwrite:
        print('\t The output file of IRAF SENSFUNC task already exits. '+sens)
        print('\t SENSFUNC is skipped.')
    else:
        if overwrite:
            print('Removing '+sens)
            os.remove(sens)
            
        iraf.sensfunc(std, sens, aperture='', ignoreaps='yes',\
                      extinction=extinction,\
                      logfile='sensfunc.log')
        print('Output file of IRAF SENSFUNC task: '+sens)
                  
    return sens, True


if __name__ == '__main__':
    # Analize argments
    parser=argparse.ArgumentParser(description=\
                'This is the reduction script for an object frame.')
    parser.add_argument('infile', help='Input file name')
    parser.add_argument('-caldir', help='Calibration directory '+
                        'containing standard star data.',default=')_.caldir')
    parser.add_argument('-noext', help='Without extinction correction',
                        action='store_true', default=False)
    parser.add_argument('-o', help='Overwrite flag', dest='overwrite',\
                        action='store_true', default=False)
    args = parser.parse_args()

    standard_sens(args.infile, caldir=args.caldir, noext=args.noext,
                  overwrite=args.overwrite)
