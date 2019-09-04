#!/home/ciaran/anaconda3/bin/python

# Author Ciaran Robb
# Aberystwyth University

# -*- coding: utf-8 -*-
"""
Created on Tue May 29 16:20:58 2018

@author: Ciaran Robb

https://github.com/Ciaran1981/Sfm

This scripts tiles large datsets for micmac and processes in parallel or sequnce depending 

This uses Malt which appear to be better for orthophoto generation

Gpu use is optional

GPU mem overload is dependent on a number of factors and does occur so will require a bit of testing
Probably best to stick to a max of no physical CPUs for nt arg

There are also issues related to the mutli thread use of image magick (used by micmac),
which are hopefully recovered in the single thread clean-up at the end. 

Usage: 
    
MaltBatch.py -folder $PWD -algo UrbanMNE -num 2,1 -zr 0.01 -nt 2 -g 0 -bbox False

Here we are are using the UrbaMNE algorithm on a 3x3 grid of tiles, using the gpu,
processing 3 tiles in parallel

"""

#import pandas as pd
import argparse
from subprocess import call#, check_call, run
from glob2 import glob
from os import path, mkdir, remove
from shutil import rmtree, move
from joblib import Parallel, delayed#, parallel_backend
#import gdal

parser = argparse.ArgumentParser()

parser.add_argument("-folder", "--fld", type=str, required=True, 
                    help="path to wrkspace")

parser.add_argument("-algo", "--algotype", type=str, required=False, 
                    help="Micmac algo type eg Forest")

parser.add_argument("-num", "--noCh", type=str, required=False, 
                    help="number of chunks in grid form eg 2,2")

parser.add_argument("-zoom", "--zmF", type=str, required=False, 
                    help="Zoom level - eg 1=1 point per pixel, 2 = 1 point per  4 pixels")

parser.add_argument("-zr", "--zrg", type=str, required=False, 
                    help="z reg term context dependent")

parser.add_argument("-ori", "--oRI", type=str, required=False, 
                    help="ori folder if not the default name of Ground_UTM")

parser.add_argument("-g", "--gp", type=bool, required=False, 
                    help="gpu use yes or no")

parser.add_argument("-nt", "--noT", type=int, required=False, 
                    help="no of tiles at a time")

parser.add_argument("-max", "--mx", type=int, required=False, 
                    help="max no of chunks to do - this is for testing with a smaller subset")

parser.add_argument("-ovLap", "--ov", type=str, required=False, default='50', 
                    help="tile overlap")


parser.add_argument("-p", "--prc", type=str, required=False, default='1', 
                    help="number of threads - default 1")

parser.add_argument("-bbox", "--bb", type=bool, required=False, default=True, 
                    help="whether or not to box terrain - default is True")

#parser.add_argument("-w", "--wind", type=str, required=False, default='5', 
#                    help="The correlation window size - default is 5")

args = parser.parse_args() 

if args.oRI is None:
   gOri= "Ground_UTM"
else:
    gOri = args.oRI

if args.algotype is None:
   algo= "UrbanMNE"
else:
    algo = args.algotype

if args.noCh is None:
    numChunks = '3,3'
else:       
    numChunks = args.noCh

if args.zrg is None:
   zregu='Regul=0.02'
else:
    zregu = 'Regul='+args.zrg
    
if args.zmF is None:
   zoomF='ZoomF=2'
else:
    zoomF = 'ZoomF='+args.zmF
    
if args.gp is None:
    mmgpu = 'mm3d'
    gP = '0'
else:
    mmgpu = '/home/ciaran/MicMacGPU/micmac/bin/mm3d'
    gP = '1'

if args.noT is None:
    mp = 4 
else:
    mp = args.noT

#if args.wind is None:
#    wnd= 5
#else:
#    wnd = args.wind


fld = args.fld

proc = args.prc
DMatch = path.join(fld, 'DMatch')
bFolder = path.join(fld, 'MaltBatch')


binList = [DMatch, bFolder]

# Some funcs for use later tile one from pymicmac

# folders to bin
for crap in binList:
    try:       
        rmtree(crap)
        
    except OSError:
        pass


mkdir(bFolder)

tLog = path.join(bFolder, "TawnyLogs")
mkdir(tLog)
mLog = path.join(bFolder, "MaltLogs")
mkdir(mLog)


# run tiling


tileIt = ['tile.py', '-i', 'Ori-'+gOri, '-e',
            'JPG', '-f', 'DMatch', '-n', 
            numChunks, '-ovLap', str(args.ov)]#, '--neighbours', '9']

call(tileIt)

# To avoid the inevitable problems with pyramids not being read
# This is a sub step in PIMs, so it is assumed the simalr(ish) principle here,
# it will solve the problem
#pyram = [mmgpu, 'MMPyram', '.*JPG', 'Ground_UTM']

#call(pyram)
#
txtList = glob(path.join(DMatch,'*.list'))
nameList = [path.split(i)[1] for i in txtList]
txtList.sort()
nameList .sort()
#list mania - I am crap at writing code
finalList = list(zip(txtList, nameList))


#rejectListB = []

# May revert to another way but lets see.....
def proc_malt(subList, subName, bFolder, gP, window='2', bbox=True):
    # Yes all this string mucking about is not great but it is better than 
    # dealing with horrific xml, when the info is so simple
    tLog = path.join(bFolder, "TawnyLogs")
#    mkdir(tLog)
    mLog = path.join(bFolder, "MaltLogs")
#    mkdir(mLog)
    flStr = open(subList).read()
    # first we need the box terrain line
    box = flStr.split('\n', 1)[0]
    # then the images
    imgs = flStr.split("\n", 1)[1]
    # If on a repeat run this should avoid problems
#    imgSeq = imgs.split()
    imgs.replace("\n", "|")
    sub = imgs.replace("\n", "|")
    print('the img subset is \n'+sub+'\n\n, the bounding box is '+box) 
    
    # Outputting mm3d output to txt as it is better to keep track of multi process log
    if bbox ==True:
        mm3d = [mmgpu, "Malt", algo,'"'+sub+'"', 'Ori-'+gOri, "DefCor=0", "DoOrtho=1",
                "SzW="+window, "DirMEC="+subName, 
                "UseGpu="+gP, zoomF, zregu, "NbProc="+proc, "EZA=1", box]
    else:
        mm3d = [mmgpu, "Malt", algo,'"'+sub+'"', 'Ori-'+gOri, "DefCor=0", "DoOrtho=1",
                "SzW="+window, "DirMEC="+subName, 
                "UseGpu="+gP, zoomF, zregu, "NbProc="+proc, "EZA=1"]
    mf = open(path.join(mLog, subName+'Mlog.txt'), "w")            
    ret = call(mm3d, stdout=mf)
    if ret != 0:        
        print(subName+" missed, will pick it up later")
        pass
    else:       
        tawny = [mmgpu, 'Tawny', "Ortho-"+subName+'/', 'RadiomEgal=1', 
                 'Out=Orthophotomosaic.tif']
        tf = open(path.join(tLog, subName+'Tlog.txt'), "w")  
        call(tawny, stdout=tf)
        mDir = path.join(fld, subName)
        oDir = path.join(fld, "Ortho-"+subName) 
#        pDir= path.join(fld, subName+"pyram")
        hd, tl = path.split(subList)
        subDir = path.join(bFolder, tl)
        mkdir(subDir)
        if path.exists(mDir):
            move(mDir, subDir)
            print('subName done')
        else:
            pass            
        if path.exists(oDir):
            move(oDir, subDir)
            print('subName mosaic done')
        else:
            pass
#        if path.exists(pDir):
#            move(pDir, subDir)
#        else:
#            pass
        #return rejectList

if args.mx is None:
    todoList = Parallel(n_jobs=mp,verbose=5)(delayed(proc_malt)(i[0], 
         i[1], bFolder, gP, window='2', bbox=args.bb) for i in finalList) 
else:
    subFinal = finalList[0:args.mx]
    todoList = Parallel(n_jobs=mp,verbose=5)(delayed(proc_malt)(i[0], 
             i[1], bFolder, gP, window='2', bbox=args.bb) for i in subFinal) 


# This is here so we have some account of anything missed due to thread/gpu mem overload issues

# 

# Please note this is a temporary quick and dirty solution 
# to which there needs to be something more robust in the end
# This repeats the above sequentially to ensure no errors occur
# (Suspect it is image magick related with muti-threading)

# get a list of what has worked
doneList = glob(path.join(bFolder, "*.list"))
doneFinal = [path.split(d)[1] for d in doneList]

# get the difference between completed and listed tiles
# set is a nice command for this purpose :D

if args.mx is None:
    rejSet = set(nameList) - set(doneFinal)
    rejList = list(rejSet)
else:
    nameList = [s[1] for s in subFinal] 
    rejSet = set(nameList) - set(doneFinal)
    rejList = list(rejSet)

if len(rejList) ==0:
    print('No tiles missed, all done!')
    pass
else:
    print('The following tiles have been missed\n')    
    [print(t) for t in rejList]
    print("\nRectifying this now...")

# make list of txt image lists so we can access the pattern through the same
# func below
#    rejtxtFinal = [path.join(fld, "DMatch", p) for p in rejList]
#    
#    finrejList = list(zip(rejtxtFinal, rejList))
#    
#    #[rmtree(k) for k in rejList]
#    
#    for f in finrejList:
#        proc_malt(f[0], f[1], bFolder)#, bbox=False)
    
    


    


