#!/usr/bin/env python
# python3 OK

import sys
import os
import shutil
import numpy as np
import subprocess
import focasifu as fi
from astropy.io import fits
import argparse
from pyraf import iraf


verbose='yes'
nsum=10
match=-10.
fwidth=4.
cradius=5.
threshold=0.
function='chebyshev'
order=6
niter=0
autowrite='no'

newaps='yes'
override='no'
refit='yes'
trace='yes'
step=5
nlost=30
addfeatures='no'
logfile='identify_dispersion.log'

def identify_each(inname, database='database', \
                    coordlist=fi.filibdir+'thar.300.dat', \
                    section_x=50, \
                    overwrite=False):

    # Not to display items in IRAF packages
    sys.stdout = open('/dev/null', 'w')
    iraf.noao()
    iraf.twodspec()
    iraf.longslit()
    sys.stdout = sys.__stdout__ # Back to the stadard output

    idfile = database + '/id' + inname
    if os.path.isfile(idfile) and overwrite == False:
        print('ID file already exists. '+idfile)
    else:
        if os.path.isfile(idfile) and overwrite == True:
            print('Removing ' + idfile)
            try:
                os.remove(idfile)
            except:
                pass

        # Creating the "section" parameter
        section = 'y '+str(section_x)
    
        iraf.identify(inname, section=section,
                  database=database, coordlist=coordlist, units='',
                  nsum=nsum, match=match, ftype='emission', fwidth=fwidth,
                  cradius=cradius, threshold=threshold,
                  function='chebyshev', order=order, sample='*',
                  niter=niter, autowrite=autowrite, cursor='')

        iraf.reidentify(inname, inname,
                    interac='no', section=section, newaps=newaps,
                    override=override, refit=refit, trace=trace,
                    step=step, shift=0, nlost=nlost, cradius=cradius,
                    threshold=threshold, addfeatures=addfeatures,
                    coordlist=coordlist, match=match, database=database,
                    logfile=logfile, plotfile='', verbose=verbose,
                    cursor='')
    return
    

def reidentify_each(refname, inname, database='database', \
                    coordlist=fi.filibdir+'thar.300.dat', \
                    section_x=50, \
                    overwrite=False):

    # Not to display items in IRAF packages
    sys.stdout = open('/dev/null', 'w')
    iraf.noao()
    iraf.twodspec()
    iraf.longslit()
    sys.stdout = sys.__stdout__ # Back to the stadard output

    idfile = database + '/id' + inname
    if os.path.isfile(idfile) and overwrite == False:
        print('ID file already exists. '+idfile)
    else:
        if os.path.isfile(idfile) and overwrite == True:
            print('Removing ' + idfile)
            try:
                os.remove(idfile)
            except:
                pass

        cdelt = fits.getval(inname+'.fits', 'CDELT2')
        # Derivering shift with respect to the reference.
        refdata = fits.getdata(refname+'.fits')
        y_ref = np.mean(refdata[:,section_x-5:section_x+5], axis=1)
        indata = fits.getdata(inname+'.fits')
        y_in = np.mean(indata[:,section_x-5:section_x+5], axis=1)
        shift = fi.cross_correlate(y_in, y_ref, sep=0.1, fit=False) 
        print('%s - %s; %.2f pix'%(refname, inname, shift))

        # Creating the "section" parameter
        section = 'y '+str(section_x)
    
        print('\t reidentify '+inname)
        iraf.reidentify(refname, inname, interac='no',
                section=section, newaps=newaps, override=override,
                refit=refit, trace=trace, step=0, shift=shift*cdelt,
                nlost=nlost, cradius=cradius, threshold=threshold,
                addfeatures=addfeatures, coordlist=coordlist, match=match,
                database=database, logfile=logfile, plotfile='',
                        verbose=verbose, cursor='')

        #Check the result
        iraf.identify(inname, section=section,
                database=database, coordlist=coordlist, units='',
                nsum=nsum, match=match, ftype='emission', fwidth=fwidth,
                cradius=cradius, threshold=threshold,
                function='chebyshev', order=order, sample='*',
                      niter=niter, autowrite=autowrite, cursor='')

        iraf.reidentify(inname, inname,
                interac='no', section=section, newaps=newaps,
                override=override, refit=refit, trace=trace,
                step=step, shift=0, nlost=nlost, cradius=cradius,
                threshold=threshold, addfeatures=addfeatures,
                coordlist=coordlist, match=match, database=database,
                logfile=logfile, plotfile='', verbose=verbose,
                cursor='')

    return

def identify_dispersion_each(basename, num, overwrite=False):

    print('\n#############################')
    print('Identifying the comparison.')

    # entering the channel image directory.
    print('\t Entering the channel image directory, \"'+fi.chimagedir+'\".')
    os.chdir(fi.chimagedir)

    hdl = fits.open(basename+'.ch12.fits')
    if not fi.check_version(hdl):
        return
    
    disperser = hdl[0].header['DISPERSR']
    filter1 = hdl[0].header['FILTER01']
    filter2 = hdl[0].header['FILTER02']
    filter3 = hdl[0].header['FILTER03']
    binfac1 = hdl[0].header['BIN-FCT1']
    binfac2 = hdl[0].header['BIN-FCT2']
    naxis1 = hdl[0].header['NAXIS1']
    datatype = hdl[0].header['DATA-TYP']
    hdl.close()

    # 300R + SO58
    if disperser == 'SCFCGRMR01' and filter1 == 'NONE' and \
       filter2 == 'SCFCFLSO58' and filter3 == 'NONE':
        dispname = '300R_SO58'
        referenceimage = 'ifu_300r.png'
        coordlist = fi.filibdir+'ifu_300r.dat'
        cdelt=-1.34*binfac2
        crpix= 1897.01/binfac2
        crval= 8115.311
        
    # 300R + L600
    if disperser == 'SCFCGRMR01' and filter1 == 'SCFCFLL600' and \
       filter2 == 'NONE' and filter3 == 'NONE':
        dispname = '300R_L600'
        referenceimage = 'ifu_300r_2nd.png'
        coordlist = fi.filibdir+'ifu_300r_2nd.dat'
        cdelt=-0.64*binfac2
        crpix= 1013.97/binfac2
        crval= 4764.8684

    # VPH850 + SO58
    if disperser == 'SCFCGRHD85' and filter1 == 'NONE' and \
       filter2 == 'SCFCFLSO58' and filter3 == 'NONE':
        dispname = 'VPH850_SO58'
        referenceimage = 'ifu_vph850.png'
        coordlist = fi.filibdir+'ifu_vph850.dat'
        cdelt=-1.17*binfac2
        crpix= 2063.78/binfac2
        crval= 8264.5225

    # VPH520
    if disperser == 'SCFCGRHD52' and filter1 == 'NONE' and \
       filter2 == 'NONE' and filter3 == 'NONE':
        dispname = 'VPH520_NONE'
        referenceimage = 'ifu_vph520.png'
        coordlist = fi.filibdir+'ifu_vph520.dat'
        cdelt=-0.39*binfac2
        crpix= 2060.51/binfac2
        crval= 5343.6

    # VPH650 + SY47
    if disperser == 'SCFCGRHD65' and filter1 == 'NONE' and \
       filter2 == 'SCFCFLSY47' and filter3 == 'NONE':
        dispname = 'VPH650+SY47'
        referenceimage = 'ifu_vph650.png'
        coordlist = fi.filibdir+'thar.vphblue.dat'
        cdelt=-0.63*binfac2
        crpix= 1495.97/binfac2
        crval= 6965.38744

    # 300B
    if disperser == 'SCFCGRMB01' and filter1 == 'NONE' and \
       filter2 == 'NONE' and filter3 == 'NONE':
        dispname = '300B_NONE'
        referenceimage = 'ifu_300b.png'
        coordlist = fi.filibdir+'ifu_300b.dat'
        cdelt=-1.34*binfac2
        crpix= 2139.69/binfac2
        crval= 5760.45669
   
    # 300B + Y47
    if disperser == 'SCFCGRMB01' and filter1 == 'NONE' and \
       filter2 == 'SCFCFLSY47' and filter3 == 'NONE':
        dispname = '300B_Y47'
        referenceimage = 'ifu_300b.png'
        coordlist = fi.filibdir+'ifu_300b.dat'
        cdelt=-1.34*binfac2
        crpix= 2139.69/binfac2
        crval= 5760.45669

    # VPH900 + SO58
    if disperser == 'SCFCGRHD90' and filter1 == 'NONE' and \
       filter2 == 'SCFCFLSO58' and filter3 == 'NONE':
        dispname = 'VPH900_SO58'
        referenceimage = 'ifu_vph900.png'
        coordlist = fi.filibdir+'ifu_vph850.dat'
        cdelt=-0.63*binfac2
        crpix= 2114.06/binfac2
        crval= 9122.99193

    # VPH450 + LL550
    if disperser == 'SCFCGRHD45' and filter1 == 'NONE' and \
       filter2 == 'SCFCFLL550' and filter3 == 'NONE':
        dispname = 'VPH450_L550'
        referenceimage = 'ifu_vph450.png'
        coordlist = fi.filibdir+'ifu_vph450.dat'
        cdelt=-0.37*binfac2
        crpix= 1989.54/binfac2
        crval= 4609.5673

    # For sky lines in an object frame
    if datatype == 'OBJECT':
        num = 0
        dispname = dispname + '_SKY'
        referenceimage = 'ifu_sky.png'
        coordlist = fi.filibdir+'ifu_skyline.dat'
    
    # showing the identification example image
    proc = subprocess.Popen(['showimage.py',fi.filibdir + referenceimage])
    print(proc)
    
    for i in range(1,25):
        hdl = fits.open(basename +'.ch%02d.fits'%i, mode='update')
        hdl[0].header['CDELT2'] = cdelt
        hdl[0].header['CRPIX2'] = crpix
        hdl[0].header['CRVAL2'] = crval
        hdl[0].header['CD2_2'] = cdelt    
        hdl[0].header['CRUNIT2']= 'Angstrom'
        hdl.close()

    # Getting a X-coodinate for the "section" parameter
    section_x = int(naxis1 / 2)

    # Copying template files to the current working directory if it exits,
    # or identifing Ch12.
    database='database'
    temp_name = 'temp_'+dispname+'_'+str(binfac2)+'_'+str(num)
    if os.path.isfile(fi.filibdir + temp_name + '.fits'):
        shutil.copy(fi.filibdir + temp_name + '.fits', '.')
        
        if not os.path.isdir(database):
            os.mkdir(database)
        shutil.copy(fi.filibdir + 'database/id' + temp_name, './'+database+'/')

        # Reidentify for ch12
        reidentify_each(temp_name, basename+'.ch12',\
                        database=database, coordlist=coordlist, \
                        section_x = section_x, overwrite=overwrite)
    else:
        # Identify for ch12
        identify_each(basename+'.ch12',\
                        database=database, coordlist=coordlist, \
                        section_x = section_x, overwrite=overwrite)
        
    # Reidentify for ch11-ch01
    for i in range(11,0,-1):
        reidentify_each(basename+'.ch%02d'%(i+1), \
                        basename+'.ch%02d'%i, \
                        database=database, coordlist=coordlist, section_x = section_x,\
                        overwrite=overwrite)

    # Reidentify for ch13-ch23
    for i in range(13,24):
        reidentify_each(basename+'.ch%02d'%(i-1), \
                        basename+'.ch%02d'%i, \
                        database=database, coordlist=coordlist, section_x = section_x,\
                        overwrite=overwrite)

    # Reidentify for ch24
    section_x = int(naxis1 / 2 + 40 / binfac1)
    reidentify_each(basename+'.ch23', \
                    basename+'.ch24', \
                    database=database, coordlist=coordlist, section_x = section_x,\
                    overwrite=overwrite)

    os.chdir('..')
    proc.terminate()
    return

def identify_dispersion(basenames, overwrite=False):
    for k in range(len(basenames)):
        identify_dispersion_each(basenames[k], k, overwrite=overwrite)
    return

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=
                    'This is the script for making each channel image.')
    parser.add_argument('comparisons',
                        help='Comma-separated comparison basenames')
    parser.add_argument('-o', help='Overwrite flag', dest='overwrite',
                        action='store_true',default=False)
    args = parser.parse_args()

    basenames = args.comparisons.split()
    identify_dispersion(basenames, overwrite=args.overwrite)
