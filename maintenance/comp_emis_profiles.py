#!/usr/bin/env python
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
    tx = 70
    for i in range(len(coo_np[:,0])):
        px = int(coo_np[i,0])
        if px == tx:
            py = int(coo_np[i,1])
            dn = coo_np[i,1] - py
            if dn == 0.0:
                plot_x = np.arange(-10.0, 10.5, 1.0)
            else:
                plot_x = np.arange(-10.0-dn, 10.0, 1.0)
            intensity = data[py-11:py+10, px]
            print(dn, plot_x)
            plt.plot(plot_x, intensity)
    plt.title(infname+" X="+str(tx))
    plt.grid()
    plt.xlim(-5,5)
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
    
