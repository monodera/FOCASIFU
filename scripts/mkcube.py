#!/usr/bin/env python
# python3 OK

import os
import focasifu as fi
import argparse
import numpy as np
from astropy.io import fits

def mkcube(basename, postfix, overwrite = False):
    print('\n#############################')
    print('Making data cube')
    hdl = fits.open(fi.chimagedir + basename+'.ch01.' +
                    postfix + '.fits')
    inhdr = hdl[0].header
    binfct1 = inhdr['BIN-FCT1']
    outfile = basename+'.xyl.fits'

    if not fi.check_version(hdl):
        return outfile, False
    
    if os.path.isfile(outfile):
        if not overwrite:
            print('Datacube file already exists. '+outfile)
            print('\t This procedure is skipped.')
            return outfile, True

    outdata = np.zeros((hdl[0].data.shape[0], 24, hdl[0].data.shape[1]),
                       dtype=np.float32)

    # Ch01 is stored in Y index 0.
    # This store order makes a non-mirror image.
    outdata[:,0,:] = hdl[0].data

    for i in range(2,25):
        hdl = fits.open(fi.chimagedir + basename+'.ch{:02d}.'.format(i) +
                        postfix + '.fits')
        outdata[:,i-1,:] = hdl[0].data
        hdl.close()

    f = open(fi.filibdir + 'edge' + str(binfct1) + '.dat')
    lines = f.readlines()
    edge_x=[]
    for i in range(2):
        cells = lines[i].split()
        edge_x.append(int(float(cells[0])))
    f.close()

    outhdu = fits.PrimaryHDU(data=outdata[:,:,edge_x[0]-3:edge_x[1]+1])
    outhdl = fits.HDUList([outhdu])
    outhdr = inhdr

    # FITS header treatment
    #binfac1 = inhdr['BIN-FCT1']
    xpixscale = 0.1075 #arcsec/pix
    ypixscale = 0.435 #arcsec/pix

    outhdr['WCSDIM'] = 3
    outhdr['CUNIT3'] = inhdr['CUNIT2']
    outhdr['CTYPE3'] = 'LINEAR  '
    outhdr['CRVAL3'] = inhdr['CRVAL2']
    outhdr['CDELT3'] = inhdr['CDELT2']
    outhdr['CRPIX3'] = inhdr['CRPIX2']
    outhdr['CD3_3'] = inhdr['CD2_2']
    outhdr['LTM3_3'] = inhdr['LTM2_2']

    outhdr['CUNIT1'] = 'deg'
    outhdr['CUNIT2'] = 'deg'
    outhdr['CTYPE1'] = 'RA---TAN'
    outhdr['CTYPE2'] = 'DEC--TAN'

    # Reference pixel coordinate is the IFU field center.
    outhdr['CRPIX1'] = int(outhdl[0].data.shape[2]/2+0.5)
    outhdr['CRPIX2'] = int(outhdl[0].data.shape[1]/2+0.5)

    # Derivation of the world coordinate of the IFU field center.
    
    # Angle between X axis and the direction from FOCAS FoV center to IFU.
    angle_to_ifu =34.39 + 4.7 # deg
    # Angular distance between FOCAS FoV center to IFU.
    dist = 0.04393 + 0.00094# deg
    
    crval1 = inhdr['OCRVAL1']
    crval2 = inhdr['OCRVAL2']
    slit_pa = inhdr['SLT-PA']
    a = slit_pa + 180.0 + angle_to_ifu
    ra_shift = dist * np.sin(np.radians(a)) / np.cos(np.radians(crval2))
    dec_shift = dist * np.cos(np.radians(a))
    #outhdr['CRVAL1'] = inhdr['OCRVAL1']
    #outhdr['CRVAL2'] = inhdr['OCRVAL2']
    outhdr['CRVAL1'] = crval1 + ra_shift
    outhdr['CRVAL2'] = crval2 + dec_shift
    
    outhdr['LTM2_2'] = 1.
    outhdr['LTM1_1'] = 1.
    outhdr['WAT1_001'] = 'wtype=tan axtype=ra'
    outhdr['WAT2_001'] = 'wtype=tan axtype=dec'
    outhdr['WAT3_001'] = 'wtype=linear label=Wavelength units=angstroms'
    
    outhdr['DISPAXIS'] = 3
    
    # Deriving IFU PA from SLIT PA.
    # 21.38 deg is derived from design.
    # 1.202 deg is correction factor derived by comparison with
    # IRAF CCMAP & CCSETWCS result.
    ifupa = inhdr['SLT-PA'] +21.38 -1.202 # degree
    outhdr['IFU-PA']=ifupa
    
    # Rotation matrix of the IFU field with respect to hte FOCAS field
    theta = np.deg2rad(270.0 - ifupa)
    rot = np.matrix([[np.cos(theta), -np.sin(theta)], \
                 [np.sin(theta), np.cos(theta)]])
    
    # Creating the new CD matrix for the reconstruction image
    xscale = xpixscale * binfct1 / 3600.0
    yscale = -ypixscale / 3600.0
    #xscale = -xpixscale * binfct1 / 3600.0
    #yscale = ypixscale / 3600.0
    outhdr['CD1_1'] = rot[0,0] * xscale
    outhdr['CD1_2'] = rot[0,1] * yscale
    outhdr['CD2_1'] = rot[1,0] * xscale
    outhdr['CD2_2'] = rot[1,1] * yscale

    outhdr.remove('CDELT1')
    outhdr.remove('CDELT2')

    outhdr['RADESYSa']='FK5'
    outhdl[0].header = outhdr
    outhdl.writeto(outfile, overwrite=overwrite)
    outhdl.close()
    hdl.close()
    print('\t Datacube file: '+outfile)
    return outfile, True


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='This is the script for making a data cube from channlel images.')
    parser.add_argument('frameid', help='Frame ID')
    parser.add_argument('postfix', help='Postfix')
    parser.add_argument('-o', help='Overwrite flag', dest='overwrite', action='store_true',default=False)
    args = parser.parse_args()

    mkcube(args.frameid, args.postfix, overwrite=args.overwrite)
