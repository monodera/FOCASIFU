#!/usr/bin/env python

from pyds9 import *
import sys

def pan_all(argv):
    DS9list = ds9_targets()

    if DS9list is None:
        d = DS9()
    else:
        d = DS9(DS9list[0])

    com = 'pan'
    for i in range(len(argv)-1):
        com = com + ' '+argv[i+1]
    print(com)
    
    frameids = d.get('frame all')    
    for i in frameids:
        d.set('frame '+str(i))
        d.set(com)
    
if __name__ == '__main__':
    pan_all(sys.argv)
