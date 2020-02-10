#!/usr/bin/env python
#
# <input fits> <output fits> <stat lambda> <end lambda>
#

from astropy.io import fits
import numpy as np
import argparse


def Wav2Pix(w, crpix, crval, cdelt):
    # w: wavelength (A)
    # crpix: reference pixel
    # crval: reference wavelength (A)
    # cdelt: waverength step per pixel (A)
    pix = (w - crval) / cdelt + crpix - 1.0
    return pix


def MonoImage(hdl, band, en):
    scidata = hdl[en].data
    hdr = hdl[en].header
    if 'CD3_3' in hdr:
        cdelt = hdr['CD3_3']
    else:
        cdelt = hdr['CDELT3']
    crpix = hdr['CRPIX3']
    crval = hdr['CRVAL3']

    pix1 = int(Wav2Pix(band[0], crpix, crval, cdelt) + 0.5)
    pix2 = int(Wav2Pix(band[1], crpix, crval, cdelt) + 0.5)

    imdata = np.sum(scidata[pix1:pix2+1,:,:], axis=0)
    pixnum = pix2 - pix1 + 1
    
    return imdata, pixnum


def LineImage(incube, outfits, onband, c1, c2, en):
    hdl = fits.open(incube)
    ondata, linepix = MonoImage(hdl, onband, en)
    if c1 is not None:
        con1data, con1pix = MonoImage(hdl, c1, en)
        if c2 is not None:
            con2data, con2pix = MonoImage(hdl, c2, en)
            linedata = ondata - (con1data / con1pix + con2data / con2pix) \
                       / 2.0 * linepix
        else:
            linedata = ondata - con1data
    else:
        linedata = ondata

    outhdu = fits.PrimaryHDU(data=linedata)
    outhdl = fits.HDUList([outhdu])
    hdr = hdl[en].header
    hdr['WCSDIM']=2

    remove_key = ['CD3_3','CD1_3', 'CD2_3', 'CD3_1', 'CD3_2', 'CDELT3',
                  'CRPIX3','CRVAL3','CUNIT3','CTYPE3', 'LTM3_3',
                  'WAT3_001', 'NAXIS3', 'XTENSION', 'EXTNAME',
                  'HDUCLAS1', 'HDUCLAS2', 'HDUVERS', 'HDUDOC', 'HDUCLASS',
                  'PCOUNT', 'GCOUNT', 'ERRDATA']
    
    for key in remove_key:
        if key in hdr:
            hdr.remove(key)
    hdr.insert(0, ('SIMPLE', True))
    outhdl[0].header = hdr
    outhdl.writeto(outfits)
    outhdl.close()
    hdl.close()
    return

    
if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=
                '')
    parser.add_argument('incube', help='Input data cube')
    parser.add_argument('outfits', help='Output fits name')
    parser.add_argument('onband', nargs=2, type=float,
                        help='Onband wavelength range (A)')
    parser.add_argument('-c1', '--continuum1', nargs=2, type=float,
                        help='Continuum1 wavelength range (A)')
    parser.add_argument('-c2', '--continuum2', nargs=2,  type=float,
                        help='Continuum1 wavelength range (A)')
    parser.add_argument('-en', '--extnum', type=int, default=0,
                        help='FITS extension number to be used. Dfault is 0.')
    args = parser.parse_args()

    LineImage(args.incube, args.outfits, args.onband, args.continuum1,
              args.continuum2, args.extnum)

