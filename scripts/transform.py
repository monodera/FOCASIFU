#!/usr/bin/env python
# python3 OK

import os
import sys
import argparse
from astropy.io import fits
# Not to display warning.
temp_stderr = sys.stderr
sys.stderr = open('/dev/null', 'w')
from pyraf import iraf
sys.stderr = temp_stderr  # Back to the stadard error output

import focasifu as fi

def transform(basename, waveref, spatialref, overwrite=False):
    # input: input fits file basename to be corrected.
    # wavefef: wavelength reference basename.
    # spatialref referrence: spatial referrence basename.
    
    print('\n#############################')
    print('Transforming')

    hdl = fits.open(basename+'.ov.fits')
    if not fi.check_version(hdl):
        return False
    if not fi.check_version_f(waveref+'.ov.fits'):
        return False
    if not fi.check_version_f(spatialref+'.fcmb.fits'):
        return False
    
    hdr = hdl[0].header
    binfct1 = hdr['BIN-FCT1']
    disperser = hdr['DISPERSR']
    filter1 = hdr['FILTER01']
    filter2 = hdr['FILTER02']
    filter3 = hdr['FILTER03']
    hdl.close()

    # entering the channel image directory.
    print('\t Entering the channel image directory, \"'+fi.chimagedir+'\".')
    os.chdir(fi.chimagedir)

    ny = 5500
    # 300R + SO58
    if disperser == 'SCFCGRMR01' and filter1 == 'NONE' and \
       filter2 == 'SCFCFLSO58' and filter3 == 'NONE':
        y1 = 5600.
        dy = 1.34
        ny = 3800
    
    # 300R + L600
    if disperser == 'SCFCGRMR01' and filter1 == 'SCFCFLL600' and \
       filter2 == 'NONE' and filter3 == 'NONE':
        y1 = 2800.
        dy = 0.636
        ny = 4000
    
    # 300B+SY47
    if disperser == 'SCFCGRMB01' and filter1 == 'NONE' and \
       filter2 == 'SCFCFLSY47' and filter3 == 'NONE':
        y1 = 4500.
        dy = 1.34
        ny = 4000
    
    # 300B + NONE
    if disperser == 'SCFCGRMB01' and filter1 == 'NONE' and \
       filter2 == 'NONE' and filter3 == 'NONE':
        y1 = 3500.
        dy = 1.34
        ny = 3500

    # VPH850 + SO58
    if disperser == 'SCFCGRHD85' and filter1 == 'NONE' and \
       filter2 == 'SCFCFLSO58' and filter3 == 'NONE':
        y1 = 5600.
        dy = 1.17
        ny = 4600

    # VPH520
    if disperser == 'SCFCGRHD52' and filter1 == 'NONE' and \
       filter2 == 'NONE' and filter3 == 'NONE':
        y1 = 4100.0
        dy = 0.39

    # VPH650+SY47
    if disperser == 'SCFCGRHD65' and filter1 == 'NONE' and \
       filter2 == 'SCFCFLSY47' and filter3 == 'NONE':
        y1 = 5200.0
        dy = 0.60

    # VPH900 + SO58
    if disperser == 'SCFCGRHD90' and filter1 == 'NONE' and \
       filter2 == 'SCFCFLSO58' and filter3 == 'NONE':
        y1 = 7400.0
        dy = 0.74

    # Not to display items in IRAF packages
    sys.stdout = open('/dev/null', 'w')
    iraf.noao()
    iraf.twodspec()
    iraf.longslit()
    sys.stdout = sys.__stdout__ # Back to the stadard output

    for i in range(1, 25):
        checkfile = basename+'.ch%02d.wc.fits'%i
        if os.path.isfile(checkfile) and not overwrite:
            print('\t '+ checkfile +' already exits. Skiped.')
        else:
            if overwrite:
                os.remove(basename+'.ch%02d.wc.fits'%i)

            iraf.transform(basename+'.ch%02d'%i, basename+'.ch%02d.wc'%i,\
                    waveref+'.ch%02d,'%i+spatialref+'.ch%02dedge'%i,\
                    interpt='linear', database='database',\
                    x1=1.0, x2='INDEF', dx=1.0, nx=int(200.0/binfct1), xlog='no',\
                    y1=y1, y2='INDEF', dy=dy, ny=ny,ylog='no',\
                    flux='no', blank=0.0, logfile='transform.log')

            hdl = fits.open(basename+'.ch%02d.wc.fits'%i, mode='update')
            hdl[0].header['COMPBASE']=(waveref, \
                                   'Frame ID of the comparison frame.')
            hdl[0].header['DISTBASE']=(spatialref, \
                                    'Frame ID used for distortion correction.')
            hdl[0].header['CUNIT2']=('Angstrom')
            hdl.close()
            print('\t '+ basename+'.ch%02d.wc.fits was created.'%i)

    print('\t Going back to the original directory.')
    os.chdir('..')
    return True


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='This is the script for transforming the image.')
    parser.add_argument('infile', help='Input file basename')
    parser.add_argument('comp', help='Comparison frame basename')
    parser.add_argument('cflat', help='Calflat frame basename')
    parser.add_argument('-o', help='Overwrite flag', dest='overwrite', action='store_true',default=False)
    args = parser.parse_args()

    transform(args.infile, args.comp, args.cflat, overwrite=args.overwrite)
