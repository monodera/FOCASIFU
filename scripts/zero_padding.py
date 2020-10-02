#!/usr/bin/env python
import argparse
import numpy as np
from astropy.io import fits


def zero_padding(infile, blank=np.nan):
    hdl = fits.open(infile, mode='update')
    data = hdl[0].data
    # Padding 0-value pixel around edges with the specified blank value.
    for j in range(data.shape[2]):
        for i in range(data.shape[1]):
            y = 0
            while data[y,i,j] == 0.0:
                data[y,i,j] = blank
                y = y + 1
                if y > data.shape[0] -1:
                    break
            y = data.shape[0] - 1
            while data[y,i,j] == 0.0:
                data[y,i,j] = blank
                y = y - 1
                if y < 0:
                    break
    hdl.close()
    return


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='This is the script'+
                                   ' for padding pixel values with NaN.')
    parser.add_argument('infile', help='Input cube file name')
    args = parser.parse_args()

    zero_padding(args.infile)
