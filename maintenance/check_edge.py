#!/usr/bin/env python2
#
# check_edge.py <id....ch??.edge>
#

from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
import re
import sys

f = open(sys.argv[1])
lines = f.readlines()
f.close()

xcoo = np.zeros((100,3))
i = 0
for line in lines:
    fields = line.split(' ')
    if fields[0] == 'begin\tidentify':
        fields2 = re.split('[\[\],]',fields[1])
        xcoo[i,0] = fields2[2]
    if fields[len(fields)-1] == 'Left\n':
        xcoo[i,1] = float(line[15:24].strip())
    if fields[len(fields)-1] == 'Right\n':
        xcoo[i,2] = float(line[15:24].strip())
        i=i+1

plt.suptitle(sys.argv[1])
plt.subplot(1,2,1)
plt.title('Left')
plt.xlabel('Y (pix)')
plt.scatter(xcoo[:i,0],xcoo[:i,1],label='Ch13 Left')
plt.grid()
plt.subplot(1,2,2)
plt.title('Right')
plt.xlabel('Y (pix)')
plt.scatter(xcoo[:i,0],xcoo[:i,2],label='Ch13 Right')
plt.grid()
plt.show()
