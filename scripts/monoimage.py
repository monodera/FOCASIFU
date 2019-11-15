#!/usr/bin/env python2
#
# <input fits> <output fits> <stat lambda> <end lambda>
#

from astropy.io import fits
import numpy as np
import sys

hdl = fits.open(sys.argv[1])
scidata = hdl[0].data
hdr = hdl[0].header
outdata = np.zeros((scidata.shape[1],scidata.shape[2]))

lambda1 = float(sys.argv[3])
lambda2 = float(sys.argv[4])
cdelt = hdr['CDELT3']
crpix = hdr['CRPIX3']
crval = hdr['CRVAL3']

pix1 = int((lambda1 - crval)/cdelt + 1)
pix2 = int((lambda2 - crval)/cdelt + 1)

#for i in range(scidata.shape[1]):
#    outdata[2*i,:] = np.mean(scidata[pix1:pix2+1,i,:],axis=0)
#    outdata[2*i+1,:] =  outdata[2*i,:]

outdata = np.mean(scidata[pix1:pix2+1,:,:],axis=0)            

outhdu = fits.PrimaryHDU(data=outdata)
outhdl = fits.HDUList([outhdu])
hdr['WCSDIM']=2
hdr.remove('CD3_3')
hdr.remove('CDELT3')
hdr.remove('CRPIX3')
hdr.remove('CRVAL3')
hdr.remove('CUNIT3')
hdr.remove('CTYPE3')
hdr.remove('LTM3_3')
hdr.remove('WAT3_001')

outhdl[0].header=hdr

outhdl.writeto(sys.argv[2])
outhdl.close()
hdl.close()
