#!/usr/bin/env python
# python3 OK

import argparse
import focasifu as fi
from astropy.io import fits
import os
import sys
# Not to display warning.
temp_stderr = sys.stderr
sys.stderr = open('/dev/null', 'w')
from pyraf import iraf
sys.stderr = temp_stderr  # Back to the stadard error output

def identify_gap(infile, overwrite=False):
    print('\n#############################')
    print('Identifying the spectrum gaps.')

    database = 'database'
    
    idfile = database + '/id' + os.path.splitext(infile)[0]
    if os.path.exists(idfile):
        if overwrite:
            os.remove(idfile)
        else:
            print('\t ID file already exists: '+idfile)
            print('\t This precedure is skipped.')
            return

    # Checking version consistency
    if not fi.check_version_f(infile):
        return
    
    # Not to display items in IRAF packages
    sys.stdout = open('/dev/null', 'w')
    iraf.noao()
    iraf.twodspec()
    iraf.longslit()
    sys.stdout = sys.__stdout__ # Back to the stadard output

    binfct1 = fits.getval(infile, 'BIN-FCT1')
    coordlist = fi.filibdir+'pseudoslitgap_binx'+str(binfct1)+'.dat'

    iraf.identify(infile, section='middle line', database=database, \
                  coordlist=coordlist, units='', nsum=20,\
                  match=-15., ftype='absorption', fwidth=16./binfct1, \
                  cradius=5.,\
                  threshold=0., function='chebyshev', order=2, sample='*', \
                  niter=0, autowrite='no')

    iraf.reidentify(infile, infile, interac='no', nsum=50, \
                    section='middle line', newaps='no', override='no',\
                    refit='yes', trace='yes', step=100, shift=0,\
                    nlost=20, cradius=5., threshold=0., addfeatures='no',\
                    coordlist=coordlist, match=-3., \
                    database=database, logfile='identify_gap.log', plotfile='', \
                    verbose='yes', cursor='')
    return


if __name__ == '__main__':
    # Analize argments
    parser=argparse.ArgumentParser(description='This is the script ' +\
                                   'for identifying spectrum gap locations.')
    parser.add_argument('-o', help='Overwrite flag', dest='overwrite', \
                        action='store_true',default=False)
    parser.add_argument('infile', help='Combined CAL flat image')
    args = parser.parse_args()

    identify_gap(args.infile, overwrite=args.overwrite)

