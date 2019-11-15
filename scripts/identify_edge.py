#!/usr/bin/env python
# python3 OK

import argparse
from astropy.io import fits
import sys
import os
import focasifu as fi
from correct_ch12_edge import correct_ch12_edge

# Not to display warning.
temp_stderr = sys.stderr
sys.stderr = open('/dev/null', 'w')
from pyraf import iraf
sys.stderr = temp_stderr  # Back to the stadard error output


def identify_edge(infile, overwrite=False):
    print('\n#############################')
    print('Identifying the edges.')

    binfct1 = fits.getval(infile, 'BIN-FCT1')
    coordlist = fi.filibdir + 'edge' + str(binfct1) +'.dat'

    section='middle line'
    verbose='yes'
    nsum=50
    match=-10.
    fwidth=6./binfct1
    cradius=20./binfct1
    threshold=0.
    function='chebyshev'
    order=2
    niter=0
    autowrite='yes'

    newaps='yes'
    override='yes'
    refit='no'
    trace='yes'
    step=50
    shift=0
    nlost=0
    minsep=60./binfct1
    addfeatures='no'
    database = 'database'
    logfile='identify_edge.log'

    # Not to display items in IRAF packages
    sys.stdout = open('/dev/null', 'w')
    iraf.noao()
    iraf.twodspec()
    iraf.longslit()
    sys.stdout = sys.__stdout__ # Back to the stadard output

    # entering the channel image directory.
    # os.chdir() does not change the directory for pyraf only in this function.
    print('\t Entering the channel image directory, \"'+fi.chimagedir+'\".')
    iraf.cd(fi.chimagedir)

    basename = fits.getval('../'+infile,'FRAMEID')

    idfile = database + '/id' + basename+'.ch01edge'
    if os.path.isfile(idfile) and not overwrite:
        print('\t Edge identification files already exist, ' + idfile \
              + '. Skipping.')
    else:
        if os.path.isfile(idfile) and overwrite:
            print('\t Removing '+idfile)
            os.remove(idfile)
        
        print('\t Identifying: '+ basename + '.ch01edge.fits')
        iraf.identify(basename + '.ch01edge',
                      section=section, database=database,
                      coordlist=coordlist, units='', nsum=nsum,
                      match=match, maxfeat=2,ftype='emission', fwidth=fwidth,
                      cradius=cradius, threshold=threshold, function=function,
                      order=order, sample='*', niter=niter, autowrite=autowrite)
        
        print('\t Reidentifying: ' + basename + '.ch01edge.fits')
        iraf.reidentify(basename + '.ch01edge', basename+'.ch01edge',
                        interac='no', section=section, newaps=newaps,
                        override=override, refit=refit, trace=trace,
                        step=step, nsum=nsum, shift=shift, nlost=nlost,
                        cradius=cradius, threshold=threshold,
                        addfeatures=addfeatures, coordlist=coordlist,
                        match=match, maxfeat=2, minsep=minsep, database=database,
                        logfile=logfile, plotfile='', verbose=verbose,
                        cursor='')

    for i in range(2,25):
        print('\t Reidentifying: ' + basename + '.ch%02dedge.fits'%i)
        idfile = database + '/id' + basename+'.ch%02dedge'%i
        if os.path.isfile(idfile) and not overwrite:
            print('\t Edge identification files already exist, '+ idfile +'. Skipping.')
        else:
            if os.path.isfile(idfile) and overwrite:
                print('\t Removing '+idfile)
                os.remove(idfile)

            # treatment for VPH650
            if i == 12:
                disperser = fits.getval(basename+'.ch12edge.fits', 'DISPERSR')
                if disperser == 'SCFCGRHD65':
                    nlost = 1
            if i == 13:
                disperser = fits.getval(basename+'.ch12edge.fits', 'DISPERSR')
                if disperser == 'SCFCGRHD65':
                    nlost = 0
                           
            iraf.reidentify(basename+'.ch%02dedge'%(i-1), \
                            basename+'.ch%02dedge'%i, \
                            interac='no', section=section, newaps=newaps, \
                            override=override, refit=refit, trace=trace, \
                            step=0.0, nsum=nsum, shift=shift, nlost=nlost, \
                            cradius=cradius, threshold=threshold, \
                            addfeatures=addfeatures, coordlist=coordlist, \
                            match=match, maxfeat=2, minsep=minsep, \
                            database=database, logfile=logfile, \
                            plotfile='', verbose=verbose, cursor='')
            #Check the result
            iraf.identify(basename+'.ch%02dedge'%i, section=section, \
                          database=database, coordlist=coordlist, units='', \
                          nsum=nsum, match=match, maxfeat=2,ftype='emission', \
                          fwidth=fwidth, cradius=cradius, threshold=threshold, \
                          function=function, order=order, sample='*', \
                          niter=niter, autowrite=autowrite)
                          
            iraf.reidentify(basename+'.ch%02dedge'%i, \
                            basename+'.ch%02dedge'%i, \
                            interac='no', section=section, newaps=newaps, \
                            override=override, refit=refit, trace=trace, \
                            step=step, nsum=nsum, shift=shift, nlost=nlost, \
                            cradius=cradius, threshold=threshold, \
                            addfeatures=addfeatures, coordlist=coordlist, \
                            match=match, maxfeat=2, minsep=minsep, \
                            database=database, logfile=logfile, \
                            plotfile='', verbose=verbose, cursor='')

    print('\t Go back to the original directory.')
    iraf.cd('..')

    disperser = fits.getval(fi.chimagedir+basename+'.ch12edge.fits', 'DISPERSR')
    if disperser == 'SCFCGRHD65':
        correct_ch12_edge(basename, overwrite=overwrite)
        
    return


if __name__ == '__main__':
    # Analize argments
    parser=argparse.ArgumentParser(description='This is the script '+\
                        'for precisely identifying spectrum edge positions.')
    parser.add_argument('infile', help='Combined CAL flat FITS file')
    parser.add_argument('-o', help='Overwrite flag', dest='overwrite', \
                        action='store_true',default=False)
    args = parser.parse_args()

    identify_edge(args.infile, overwrite=args.overwrite)
