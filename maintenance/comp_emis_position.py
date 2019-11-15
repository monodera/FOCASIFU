#!/usr/bin/env python2
# python3 ok

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import re
import numpy as np
from astropy.io import fits
import argparse

def comparison_emission_position(infname):
    # Getting image data
    data = fits.getdata('chimages/'+infname)

    # Reading ID-file
    rootname = infname[:len(infname)-5]
    f = open('chimages/database/id' + rootname)
    lines = f.readlines()
    f.close()

    coo = []
    for i in range(len(lines)):
        fields = re.split('[,\[\t\n]',lines[i])
        if fields[0] == 'begin':
            x = float(fields[2])
        elif fields[1] == 'features':
            n = int(fields[2])
            for j in range(n):
                i += 1
                fields = lines[i].split()
                y = float(fields[0])
                coo.append([x, y])
            
    coo_np = np.array(coo)

    # Plotting
    plt.imshow(data, origin='bottom', norm=LogNorm(vmin=1,vmax=np.max(data)), \
               aspect='auto')
    plt.scatter(coo_np[:,0]-1,coo_np[:,1]-1, c='red', s=5)
    plt.xlabel('X (pix)')
    plt.ylabel('Y (pix)')
    plt.title(infname)
    plt.show()
    return


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description= \
            'This is the script for checking the identified positions of '+
            'the comparison lines.')
    parser.add_argument('ifname',\
                    help='Input FITS file')
    args = parser.parse_args()

    comparison_emission_position(args.ifname)
    
