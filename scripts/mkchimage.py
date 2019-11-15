#!/usr/bin/env python
# python3 OK

import focasifu as fi
import argparse
import os
from astropy.io import fits
from extract import extract, writetochimages

def mkchimage(infile, calflat_basename, overwrite=False):
    print('\n#############################')
    print('Making channel images')

    if not os.path.isdir(fi.chimagedir):
        os.mkdir(fi.chimagedir)

    inhdl = fits.open(infile)
    inhdr = inhdl[0].header
    basename = inhdr['FRAMEID']
    
    if not fi.check_version(inhdl):
        return basename, False
    
    if os.path.isfile(fi.chimagedir + basename+'.ch01.fits'):
        if overwrite:
            for i in range(1,25):
                try:
                    os.remove(fi.chimagedir + basename+'.ch%02d.fits'%i)
                except:
                    pass                    
        else:
            print('\t Extracted frames already exit. ' + fi.chimagedir + basename+\
                  '.ch01.fits')
            print('\t This procedure is skipped.')
            inhdl.close()
            return basename, True

    # Extracting each spectrum and storing to the cubehdl
    gapcoef_file =  calflat_basename +'.fcmb.gapcoef'
    cubehdl = extract(inhdl,gapcoef_file)
    writetochimages(cubehdl, basename, overwrite=overwrite)

    cubehdl.close()
    inhdl.close()
    return basename, True


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='This is the script for making each channel image.')
    parser.add_argument('infile', help='Input file')
    parser.add_argument('cflat', help='CAL flat basename')
    parser.add_argument('-o', help='Overwrite flag', dest='overwrite', action='store_true',default=False)
    args = parser.parse_args()

    mkchimage(args.infile, args.cflat, overwrite=args.overwrite)
