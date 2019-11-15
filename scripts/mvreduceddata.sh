#!/bin/sh
mv *.ov.fits $1
mv *.fcmb* $1
mv *.ch??.fits $1
mv *.ch??edge.fits $1
mv *.ch??.wc.fits $1
mv *.cr.fits $1
mv *.mask.fits $1
mv *.xyl.fits $1
mv *.ss.fits $1
mv *.ff.fits $1
mv database/* $1/database/
mv *.log $1

