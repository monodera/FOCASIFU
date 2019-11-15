#!/usr/bin/env python2

from pyds9 import *

DS9list = ds9_targets()
d = DS9(DS9list[0])

cells=['','','']

while cells[0] != 'q':
    c = d.get('iexam key coordinate physical')
    cells = c.split()
    x = int(float(cells[1])+0.5)
    y = int(float(cells[1])+0.5)
    if cells[0] != 'Up' != cells[0]!='Down' and cells[0]!='Left' and cells[0]!='Right':
        print('['+str(int(float(cells[1])+0.5)) + ', '+\
              str(int(float(cells[2])+0.5))+'],')
