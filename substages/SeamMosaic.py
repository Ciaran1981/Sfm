#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 14:45:35 2019

@author: ciaran


SeamMosaic.py -folder PIMs-Ortho -algo Fraser  

Use the micmac teslib seamline mosaicing function - which requires a labourious

image pattern so have used python here as typing is so strenuous


"""



#import pandas as pd
import argparse
from subprocess import call
from glob2 import glob
from os import path, chdir

parser = argparse.ArgumentParser()

parser.add_argument("-folder", "--fld", type=str, required=True, 
                    help="working folder with imagery - this will be a Malt-Ortho or PIMs-Ortho folder")

parser.add_argument("-algo", "--algotype", type=str, required=False, 
                    help="")



args = parser.parse_args() 

if args.algotype is None:
   algo= "Fraser"
else:
    algo = args.algotype
       

fld = args.fld


imList = glob(path.join(fld, "*Ort_*.tif"))
imList.sort()


subList = [path.split(item)[1] for item in imList]

subStr = str(subList)

sub2 = subStr.replace("[", "")
sub2 = sub2.replace("]", "")
sub2 = sub2.replace("'", "") 
sub2 = sub2.replace(", ", "|")      

chdir(fld)           

mm3d = ["mm3d", "TestLib", "SeamlineFeathering", '"'+sub2+'"',  "Out=SeamMosaic.tif"]

#"ApplyRE=1"
call(mm3d)


"""
# TODO
# Here follows the approx code for the py implementation 
pairs = [("orthopath1", "orthopath2"), ("orthopath1", "orthopath2")]

# Observations used to adjust the overall model of the pair
obsGlob = ?? (i,j) # this seems to imply a pixel coord or block

# Observations used to calculate a mean image equalization model
obsMn = ??

# Must open stuff and set the block size

inDataset = gdal.Open(inputIm)

    
outDataset = _copy_dataset_config(inputIm, outMap = outputIm,
                             bands = inDataset.RasterCount)
bnd = inDataset.GetRasterBand(1)

outBand = outDataset.GetRasterBand(1)
cols = inDataset.RasterXSize
rows = inDataset.RasterYSize
# So with most datasets blocksize is a row scanline
if blocksize == None:
    blocksize = bnd.GetBlockSize()
    blocksizeX = blocksize[0]
    blocksizeY = blocksize[1]
else:
    blocksizeX = blocksize
    blocksizeY = blocksize

# loop

for p in pairs:
  # use the usual gdal routine here range (i, j)
    
    for i in tqdm(range(0, rows, blocksizeY)):
            if i + blocksizeY < rows:
                numRows = blocksizeY
            else:
                numRows = rows -i
        
            for j in range(0, cols, blocksizeX):
                if j + blocksizeX < cols:
                    numCols = blocksizeX
                else:
                    numCols = cols - j

               
                array = bnd.ReadAsArray(j, i, numCols, numRows)
                
                # pseudo of what is to be done
                #RadiomTuileImagei=a+b∗RadiomTuileImagj
                #Obs1tuile= (a+b∗Quartile1(RadiomTuileImagej), Quartile1(RadiomTuileImagej)
                #Obs2tuile= (a+b∗Quartile3(RadiomTuileImagej), Quartile3(RadiomTuileImagej)
                
                #AjoutObs1tuileàObsGlobi,i
                #AjoutObs2tuileàObsGlobi,j
                # this loop ends
            RadiomImagei=a+b∗RadiomImage
            Obs1ImCpl= (a+b∗Quartile1(RadiomImagej), Quartile1(RadiomImagej)
            Obs2ImCpl= (a+b∗Quartile3(RadiomImagej), Quartile3(RadiomImagej)
            AjoutObs1ImCplàObsGlobImii
            AjoutObs1ImCplàObsGlobImii
                #outBand.WriteArray(array, j, i) 
        
""" 
 









































