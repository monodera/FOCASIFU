#!/usr/bin/env python
# python3 OK

import sys
import os
import focasifu as fi
from astropy.io import fits
import argparse
# Not to display warning.
temp_stderr = sys.stderr
sys.stderr = open('/dev/null', 'w')
from pyraf import iraf
sys.stderr = temp_stderr  # Back to the stadard error output


def fitcoord_dispersion(basenames, overwrite=False):

    print('\n#############################')
    print('Getting the dispersion map.')

    # entering the channel image directory.
    print('\t Entering the channel image directory, \"'+fi.chimagedir+'\".')
    os.chdir(fi.chimagedir)

    database='database'
    function='chebyshev'
    xorder=7
    yorder=7
    logfiles='STDOUT,fitcoord_dispersion.log'
    # for multi-comparison images
    combine = 'yes'


    # Not to display items in IRAF packages
    sys.stdout = open('/dev/null', 'w')
    iraf.noao()
    iraf.twodspec()
    iraf.longslit()
    sys.stdout = sys.__stdout__ # Back to the stadard output

    for i in range(1,25):
        fcfile = basenames[0] + '.ch%02d'%i
        if os.path.isfile(database + '/fc' + fcfile) and overwrite == False:
            print('\t FC file already exits: ' + fcfile)
        else:
            if os.path.isfile(database + '/fc' + fcfile) and overwrite == True:
                print('Removing ' + fcfile)
                os.remove(database + '/fc' + fcfile)
                
            infiles = ''
            for basename in basenames:
                infiles = infiles + basename + '.ch%02d,'%i
            
            iraf.fitcoord(infiles[:len(infiles)-1], fitname=fcfile, interactive='yes', \
                    combine=combine, database=database, deletions='',\
                    function = function,xorder=xorder, yorder=yorder,\
                    logfiles=logfiles, graphics='stdgraph', cursor='')

    print('Going back to the original directory.')
    os.chdir('..')
    return


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='This is the script for making each channel image.')
    parser.add_argument('comparisons', help='Comma-separated comparison basenames')
    parser.add_argument('-o', help='Overwrite flag', dest='overwrite', action='store_true',default=False)
    args = parser.parse_args()
    
    fitcoord_dispersion(args.comparisons, overwrite=args.overwrite)
