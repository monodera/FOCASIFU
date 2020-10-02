#!/usr/bin/env python

from pyds9 import *
import argparse


def check_cr(image1, image2, zoom=2):
    DS9list = ds9_targets()

    if DS9list is None:
        d = DS9()
    else:
        d = DS9(DS9list[0])

    d.set('tile yes')
    d.set('tile grid layout 3 2')
    d.set('view layout vertical')

    d.set('frame 1')
    d.set('fits '+image1+'.ov.fits')
    d.set('mask color red')
    d.set('fits mask '+image1+'.mask.fits')
    d.set('zoom to '+str(zoom))
    d.set('scale zscale')
    
    d.set('frame 2')
    d.set('fits '+image1+'.cr.fits')
    d.set('zoom to '+str(zoom))
    d.set('scale zscale')

    d.set('frame 3')
    d.set('fits '+image1+'.ov.fits')
    d.set('zoom to '+str(zoom))
    d.set('scale zscale')

    
    d.set('frame 4')
    d.set('fits '+image2+'.ov.fits')
    d.set('mask color red')
    d.set('fits mask '+image2+'.mask.fits')
    d.set('zoom to '+str(zoom))
    d.set('scale zscale')
    
    d.set('frame 5')
    d.set('fits '+image2+'.cr.fits')
    d.set('zoom to '+str(zoom))
    d.set('scale zscale')

    d.set('frame 6')
    d.set('fits '+image2+'.ov.fits')
    d.set('zoom to '+str(zoom))
    d.set('scale zscale')

    
if __name__ == '__main__':
    parser=argparse.ArgumentParser(description= \
            'This is the script for checking cosmic ray removing.')
    parser.add_argument('image1', help='Frame ID1')
    parser.add_argument('image2', help='Frame ID2')
    parser.add_argument('-zoom', help='Zoom: default is 4.',
                        type=int, default=2)
    args = parser.parse_args()
    check_cr(args.image1, args.image2, args.zoom)
