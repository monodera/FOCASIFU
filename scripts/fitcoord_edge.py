#!/usr/bin/env python3
# python3 OK

import argparse
from astropy.io import fits
import sys
import os
import focasifu as fi
# Not to display warning.
temp_stderr = sys.stderr
sys.stderr = open('/dev/null', 'w')
from pyraf import iraf
sys.stderr = temp_stderr  # Back to the stadard error output

def fitcoord_edge(infile, overwrite=False):
    print('\n#############################')
    print('Getting the distortion map.')

    # entering the channel image directory.
    print('\t Entering the channel image directory, \"'+fi.chimagedir+'\".')
    os.chdir(fi.chimagedir)

    basename = fits.getval('../'+infile, 'FRAMEID')
    for j in range(1, 25):
        fitcoord_edge_each(basename+'.ch%02dedge'%j, overwrite=overwrite)
    print('\t Go back to the original directory.')
    os.chdir('..')
    return
        
def fitcoord_edge_each(fname, overwrite=False):
    nteractive='yes'
    database= 'database'
    function='chebyshev'
    xorder=2
    yorder=7
    logfiles='STDOUT,fitcoord_edge.log'
    interactive='yes'
    cursor =''
    #    cursor = filibdir+'fitcoord_edge.cur'

    idfile = database + '/id' + fname
    if not os.path.isfile(idfile):
        print('\t Edge identification files do not exist. ' + idfile)
        return

    fcfile = database + '/fc' + fname
    if os.path.isfile(fcfile) and not overwrite:
        print('\t Edge fitcoord files already exist. ' + fcfile)
        print('\t This procedure is skipped.')
        return

    # Not to display items in IRAF packages
    sys.stdout = open('/dev/null', 'w')
    iraf.noao()
    iraf.twodspec()
    iraf.longslit()
    sys.stdout = sys.__stdout__ # Back to the stadard output

    iraf.fitcoord(fname, fitname='', interactive=interactive, \
                  combine='no', database=database, deletions='',\
                  function = function,xorder=xorder, yorder=yorder,\
                  logfiles=logfiles, graphics='stdgraph', cursor=cursor)

    return


if __name__ == '__main__':
    # Analize argments
    parser=argparse.ArgumentParser(description='This is the script for precisely identifying spectrum edge positions.')
    parser.add_argument('infile', help='Combined CAL flat FITS file')
    parser.add_argument('-o', help='Overwrite flag', dest='overwrite', action='store_true',default=False)
    args = parser.parse_args()

    fitcoord_edge(args.infile, overwrite=args.overwrite)
