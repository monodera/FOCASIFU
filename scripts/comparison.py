#!/usr/bin/env python
# python3 OK
#
    
import focasifu as fi
import argparse
from astropy.io import fits
from bias_overscan import bias_overscan
from mkchimage import mkchimage
from identify_dispersion import identify_dispersion
from fitcoord_dispersion import fitcoord_dispersion

def comparison(comparisons, calflat, rawdatadir='', overwrite=False):

    basenames = []
    temp_basenames = ''
    for infile in comparisons.split(','):
        ovname, stat = bias_overscan(infile, rawdatadir=rawdatadir,\
                                     overwrite=overwrite)
        if stat == False:
            return
        
        basename, stat = mkchimage(ovname, calflat, overwrite=overwrite)
        if stat == True:
            basenames.append(basename)
        else:
            return
            
    identify_dispersion(basenames, overwrite=overwrite)
    fitcoord_dispersion(basenames, overwrite=overwrite)

    return

if __name__ == '__main__':
    # Usage: comparison <comparison> <CAL flat> 
    # comparison: comparison files
    # CAL flat: flat file
    
    parser=argparse.ArgumentParser(description='This is the script for making a combined domeflat frame.    ')
    parser.add_argument('comparisons', help='Commpa-separated comparison frames')
    parser.add_argument('calflat', help='Combined CAL flat frame ID')
    parser.add_argument('-d', help='Raw data directroy', dest='rawdatadir', action='store', default='')
    parser.add_argument('-o', help='Overwrite flag', dest='overwrite', action='store_true',default=False)
    args = parser.parse_args()

    comparison(args.comparisons, args.calflat, \
               rawdatadir = args.rawdatadir, overwrite = args.overwrite)

    
