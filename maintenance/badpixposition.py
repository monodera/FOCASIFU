#!/usr/bin/env python
#
# This is the script for making a mask image
# for the decomposition of a dome flat image.
#
# badpixposition.py flat_fcmb.fits dust.fits -h high.fits
#
from pyds9 import *
import sys
import os
import shutil
from astropy.io import fits
import time
import argparse
import numpy as np

panpixels = 500

def getkey(d):
    a = d.get('iexam key coordinate image')
    b = a.split()
    key = b[0]
    x = int(float(b[1])+0.5)
    y = int(float(b[2])+0.5)
    return key, x, y

def mkbadpiximage(flat, dust, high=None):
    DS9list = ds9_targets()

    if DS9list is None:
        d = DS9()
    else:
        d = DS9(DS9list[0])

    tempfile = 'temptemp.fits'
    if os.path.isfile(tempfile):
        os.remove(tempfile)

    if not os.path.isfile(dust):
        data = fits.getdata(flat)
        datanew = np.zeros(data.shape, dtype=np.int16)
        outhdu = fits.PrimaryHDU(data=datanew)
        outhdl = fits.HDUList([outhdu])
        outhdl.writeto(tempfile)
    else:
        shutil.copyfile(dust, tempfile)
    
    hdl = fits.open(tempfile, mode='update')
    scidata = hdl[0].data

    if high is None:
        d.set('frame 1')
        d.set('fits '+flat)
        d.set('mask color red')
        d.set('fits mask '+tempfile)
        d.set('frame first')
    else:
        d.set('frame 1')
        d.set('fits '+high)
        d.set('mask color red')
        d.set('fits mask '+tempfile)
        d.set('frame 2')
        d.set('fits '+flat)
        d.set('scale zscale')
        d.set('frame first')
        

    key=''
    zflag = 0
    while key is not 'q':
        try:
            key, x, y = getkey(d)
        except:
            key=''
            print('Out of image area')

        if key == 'd':
            scidata[y-1,x-1] = 1
            d.set('frame refresh')
        elif key == 'u':
            scidata[y-1,x-1] = 0
            d.set('frame refresh')
        #elif key == 'Down':
        #    frameids = d.get('frame all')
        #    for frameid in frameids.split():
        #        d.set('frame '+frameid)
        #        d.set('pan 0 %d image'%panpixels)
        #    d.set('frame first')
        #elif key == 'Up':
        #    frameids = d.get('frame all')
        #    for frameid in frameids.split():
        #        d.set('frame '+frameid)
        #        d.set('pan 0 -%d image'%panpixels)
        #    d.set('frame first')
        elif key is 's':
            print('Writing')
            hdl.writeto(dust, overwrite=True)
        elif key is 'c':
            frameids = d.get('frame all')
            for frameid in frameids.split():
                d.set('frame '+frameid)
                d.set('pan to %d %d'%(x,y))
                coord = d.get('pan')
        elif key is 'z':
            frameids = d.get('frame all')
            if zflag == 0:
                for frameid in frameids.split():
                    d.set('frame '+frameid)
                    d.set('pan to %d %d'%(x,y))
                    d.set('zoom to 4')
                    coord = d.get('pan')
                    zflag = 1
                    print('zoom in '+coord)
            else:
                for frameid in frameids.split():
                    d.set('frame '+frameid)
                    d.set('pan to '+coord)
                    d.set('zoom to 1')
                    print('zoom out '+coord)
                    zflag = 0
        elif key is 'h':
            print('d: Toggle bad pixel flag')
            print('u: Untoggle bad pixel flag')
            print('Down: Pan dawn by %d pixels'%panpixels)
            print('Up: Pan up by %d pixels'%panpixels)
            print('z: Zoom up/Reset zooming')
            print('s: Save the bad pixel image')
            print('q: Quit')
        else:
            print(key)
        time.sleep(0.5)

    inkey = input('Save the bad pixel image? [y/n]')
    if inkey is 'y':
        print('Writing')
        hdl.writeto(dust, overwrite=True)

    hdl.close()
    os.remove(tempfile)

    return

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description= \
            'This is the script for making a dust image.')
    parser.add_argument('-high', help='High frequency image',\
                        action='store_true', default=None)
    parser.add_argument('flat', help='Flat image')
    parser.add_argument('dust', help='Output dust image')
    args = parser.parse_args()

    mkbadpiximage(args.flat, args.dust, high=args.high)

