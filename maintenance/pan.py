#!/usr/bin/env python2

from pyds9 import *

DS9list = ds9_targets()
d = DS9(DS0list[0])

print(d.get('frame all'))
