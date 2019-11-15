#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import sys

plt.figure(figsize=(12,4))
img=mpimg.imread(sys.argv[1])
plt.imshow(img,aspect='auto',interpolation='spline16')
plt.subplots_adjust(left=0.0, right=1.0,top=1.0,bottom=0.0)
plt.show()
