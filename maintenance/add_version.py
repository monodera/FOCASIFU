#!/usr/bin/env python2

import sys
import os
from astropy.io import fits

sys.path.append(os.path.join(os.path.dirname(__file__), '../script')) 

import focasifu as fi

hdl = fits.open(sys.argv[1], mode='update')
hdl[0].header[fi.ifu_soft_key] = fi.version
hdl.close()
