#!/usr/bin/env python

import numpy as np
import re
import os
import argparse
import focasifu as fi
from numpy.polynomial.chebyshev import chebval
import matplotlib.pyplot as plt

def correct_ch12_edge(basename, overwrite=False):
    # Correcting left edge position data of Ch12 in id-file
    print('#############################')
    print('\t Special treatment for VPH650 data.')
    print('\t Correcting left-edge-position data of Ch12')
    
    os.chdir(fi.chimagedir+'database')
    
    orgfname = 'id' + basename + '.ch12edge_org'
    if os.path.exists(orgfname) and overwrite == False:
        print(orgfname + ' has already existed.')
        os.chdir('../..')
        return

    # Picking up edge data of all channels from their id-files.
    # coo array: (ch-number, datanumber, [0:Y coodinate, 1:Left, 2:Right])
    coo = np.zeros((24,100,3))
    for j in range(24):
        fname = 'id' + basename + '.ch%02dedge'%(j+1)
        f = open(fname)
        lines = f.readlines()
        f.close()

        datanum = 0
        for line in lines:
            fields = line.split()
            if  len(fields) != 0:
                if fields[0] == 'begin':
                    fields2 = re.split('[\[\],]',fields[2])
                    coo[j,datanum,0] = float(fields2[2])
            if len(fields) == 7:
                if fields[6] == 'Left':
                    coo[j,datanum,1] = float(fields[0])
                if fields[6] == 'Right':
                    coo[j,datanum,2] = float(fields[0])
                    datanum = datanum + 1

    # Reading the id-file for Ch12.
    fname = 'id' + basename + '.ch12edge'
    f = open(fname)
    lines = f.readlines()
    f.close()

    # Creating the new id-file
    x = np.array(range(1,25))
    newlines = []
    lines_length = len(lines)
    
    for i in range(lines_length):
        fields = re.split('[\t\[\],]', lines[i])
        if fields[0] == 'begin':
            linenum = float(fields[3])
            for j in range(6):
                newlines.append(lines[i+j-1])
                
            y = np.zeros(24) # spectrum width of ch01-24
            w = np.zeros(24, dtype=np.int) # weight for fitting
            for j in range(24):
                for k in range(100):
                    if linenum == coo[j,k,0]:
                        #print(j, coo[j,k,:])
                        y[j] = coo[j,k,2] - coo[j,k,1]
                        w[j] = 1
                        
            # Ch12 width is estimated from Chebyshev fitting for the ohter channels.
            # Ch01, Ch12 and Ch24 are not used for fitting.
            w[0]=0
            w[11]=0
            w[23]=0
            
            c, weight1, stat = fi.cheb1Dfit(x,y,order=2, weight=w, \
                                niteration=2, high_nsig=3.0, low_nsig=3.0)
            if not stat:
                print('Warnning in fitting in correct_ch12_edge.py')
            ch12width = chebval(12,c)
            #yy = chebval(x,c)
            #plt.scatter(x,y)
            #plt.plot(x,yy)
            #plt.title(str(linenum))
            #plt.xlabel('Ch number')
            #plt.ylabel('Spectrum width (pix)')
            #plt.grid()
            #plt.show()

            # Generating the id-file format
            fields6 = lines[i+6].split()
            #print(fields6)
            if fields6[2] == '6.':  # If Left edge is detected,
                fields7 = lines[i+7].split()
                #print(fields7)
                if fields7[2] == '66.': # and if Right is also detected,
                    right = float(fields7[0])
                    left = right - ch12width
                    newlines.append(lines[i+5]) #  add the line for the feature number
                    newlines.append('	          %.2f         6.         6.   3.0 1 1 Left\n'%left)
                    newlines.append(lines[i+7]) #  add the line for the right edge
                    j = 0
                    flag = True
                    while flag and i+8+j < lines_length:
                        fields8 = lines[i+8+j].split()
                        if len(fields8) == 0:
                            newlines.append(lines[i+8+j])
                            j += 1
                        else:
                            if fields8[0] != '#':
                                newlines.append(lines[i+8+j])
                                j += 1
                            else:
                                flag = False

            elif fields6[2] == '66.':  # If Left edge is not detected, then
                right = float(fields6[0])
                left = right - ch12width
                newlines.append('	features	2\n') #  The feature number is changed to 2.
                newlines.append('	          %.2f         6.         6.   3.0 1 1 Left\n'%left)
                newlines.append(lines[i+6][:48]+'Right\n')  #  add the line for the right edge
                j = 0
                flag = True
                while flag and i+7+j < lines_length:
                    fields7 = lines[i+7+j].split()
                    if len(fields7) == 0:
                        newlines.append(lines[i+7+j])
                        j += 1
                    else:
                        if fields7[0] != '#':
                            newlines.append(lines[i+7+j])
                            j += 1
                        else:
                            flag = False

    # Rename the original file
    print('\t Rname ' + fname + ' to ' + orgfname)
    os.rename(fname, orgfname)

    # Saving the id-file
    print('\t Creating the new id-file, '+ fname)
    f = open(fname, 'w')
    f.writelines(newlines)
    f.close()
    
    os.chdir('../..')
    return

if __name__ == '__main__':
    # Analize argments
    parser=argparse.ArgumentParser(description='This is the script '+\
                        'for correcting the ch12 left edge data in id-file.')
    parser.add_argument('inbase', help='Basename of the combined CAL flat FITS file')
    parser.add_argument('-o', help='Overwrite flag', dest='overwrite', \
                        action='store_true',default=False)
    args = parser.parse_args()

    correct_ch12_edge(args.inbase, overwrite=args.overwrite)
