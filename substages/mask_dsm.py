#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  5 12:45:39 2018

@author: ciaran

usage:
    mask_dsm.py -folder $PWD -n 4 -z 8 -m 7
"""

import gdal
import argparse
from glob2 import glob
import os
from tqdm import tqdm
from joblib import Parallel, delayed
import numpy as np

# Most of this is taken from geospatial_learn and is here for convenience
# https://github.com/Ciaran1981/geospatial-learn
# The lib function is more flexible than this script which is here to a masking operation specific to MicMac

def _copy_dataset_config(inDataset, FMT = 'Gtiff', outMap = 'copy',
                          bands = 1):
    """Copies a dataset without the associated rasters.

    """
    if FMT == 'HFA':
        fmt = '.img'
    if FMT == 'KEA':
        fmt = '.kea'
    if FMT == 'Gtiff':
        fmt = '.tif'
    
    x_pixels = inDataset.RasterXSize  # number of pixels in x
    y_pixels = inDataset.RasterYSize  # number of pixels in y
    geotransform = inDataset.GetGeoTransform()
    PIXEL_SIZE = geotransform[1]  # size of the pixel...they are square so thats ok.
    #if not would need w x h
    x_min = geotransform[0]
    y_max = geotransform[3]
    # x_min & y_max are like the "top left" corner.
    projection = inDataset.GetProjection()
    geotransform = inDataset.GetGeoTransform()   
    #dtype=gdal.GDT_Int32
    driver = gdal.GetDriverByName(FMT)
    
    dtype = gdal.GDT_Float32
    
    # Set params for output raster
    outDataset = driver.Create(
        outMap+fmt, 
        x_pixels,
        y_pixels,
        bands,
        dtype)

    outDataset.SetGeoTransform((
        x_min,    # 0
        PIXEL_SIZE,  # 1
        0,                      # 2
        y_max,    # 3
        0,                      # 4
        -PIXEL_SIZE))
        
    outDataset.SetProjection(projection)
    
    return outDataset

def mask_raster_multi(inputIm,  mval=1, outval = None, mask=None,
                    blocksize = 256, FMT = None, dtype=None):
    """ 
    Perform a numpy masking operation on a raster where all values
    corresponding to  mask value are retained - does this in blocks for
    efficiency on larger rasters
    
    Parameters 
    ----------- 
    
    inputIm : string
              the granule folder 
        
    mval : int
           the masking value that delineates pixels to be kept
        
    outval : numerical dtype eg int, float
              the areas removed will be written to this value default is 0
        
    mask : string
            the mask raster to be used (optional)
        
    FMT : string
          the output gdal format eg 'Gtiff', 'KEA', 'HFA'
        
        
    blocksize : int
                the chunk of raster read in & write out

    """

    if FMT == None:
        FMT = 'Gtiff'
        fmt = '.tif'
    if FMT == 'HFA':
        fmt = '.img'
    if FMT == 'KEA':
        fmt = '.kea'
    if FMT == 'Gtiff':
        fmt = '.tif'
    
    
    if outval == None:
        outval = 0
    
    inDataset = gdal.Open(inputIm, gdal.GA_Update)
    bands = inDataset.RasterCount
    
    bnnd = inDataset.GetRasterBand(1)
    cols = inDataset.RasterXSize
    rows = inDataset.RasterYSize

    
    
    # So with most datasets blocksize is a row scanline, but 256 always seems 
    # quickest - hence it is specified above as default
    if blocksize == None:
        blocksize = bnnd.GetBlockSize()
        blocksizeX = blocksize[0]
        blocksizeY = blocksize[1]
    else:
        blocksizeX = blocksize
        blocksizeY = blocksize
    
    if mask != None:
        msk = gdal.Open(mask)
        maskRas = msk.GetRasterBand(1)
        
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
                mask = maskRas.ReadAsArray(j, i, numCols, numRows)
                if mval not in mask:
                    array = np.zeros(shape=(numRows,numCols), dtype=np.int32)
                    for band in range(1, bands+1):
                        bnd = inDataset.GetRasterBand(band)
                        array = bnd.ReadAsArray(j, i, numCols, numRows)
                        array[mask != mval]=0
                        array[array <= 0]=0
                        bnd.WriteArray(array, j, i)
                else:
                    
                    for band in range(1, bands+1):
                        bnd = inDataset.GetRasterBand(band)
                        array = bnd.ReadAsArray(j, i, numCols, numRows)
                        array[mask != mval]=0
                        array[array < 0]=0
                        bnd.WriteArray(array, j, i)
                        
    else:
             
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
                    for band in range(1, bands+1):
                        bnd = inDataset.GetRasterBand(1)
                        array = bnd.ReadAsArray(j, i, numCols, numRows)
                        array[array != mval]=0
                        if outval != None:
                            array[array == mval] = outval     
                            bnd.WriteArray(array, j, i)

        inDataset.GetRasterBand(1).SetNoDataValue(0)
           
        inDataset.FlushCache()
        inDataset = None
        
#MAIN script------------------------------------------------------------------        
parser = argparse.ArgumentParser()




parser.add_argument("-folder", "--fld", type=str, required=True, 
                    help="input dsm")

parser.add_argument("-n", "--cores", type=int, required=False, 
                    help="no of cpu jobs")

parser.add_argument("-z", "--zoom", type=str, required=False, 
                    help="zoom no eg 2")

parser.add_argument("-m", "--mask", type=str, required=False, 
                    help="mask no - you may need to look at a tile folder to find out which is the matching one")

parser.add_argument("-pims", "--pms", type=bool, required=False, 
                    help="if looking for output from DronePIMs.sh/pims_subset.py")


args = parser.parse_args() 

# This conditional stuff is all hideous but will do the job until I have time to do something better

fl = args.fld

if args.cores is None:
    noJ=-1
else:
    noJ = args.cores

if args.zoom is None:
    zoomF='2'
else:
    zoomF = args.zoom
    
if args.mask is None:
    maskN ='6'
else:
    maskN = args.mask
    
if int(zoomF) == 1:
    extraNum='8'
else:
    extraNum='7'
#
if args.pms is None:
    pim = False
else:
    pim = True
#    
if pim is True:
    wildCard1 = "PIMsBatch/*tile*/DSM*.tif"
    wildCard2 = "PIMsBatch/*tile*/Masq*.tif"
    fileListIm = glob(os.path.join(fl, wildCard1))
    fileListMsk = glob(os.path.join(fl, wildCard2))
    
    if len(fileListIm) == 0:
        wildCard1 = "PIMs-TmpBasc/PIMs-Merged_Prof.tif"
        wildCard2 = "PIMs-TmpBasc/PIMs-Merged_Masq.tif"
        fileListIm = glob(os.path.join(fl, wildCard1))
        fileListMsk = glob(os.path.join(fl, wildCard2))
        

    fileListIm.sort()
    fileListMsk.sort()


    finalList = list(zip(fileListIm, fileListMsk))

    Parallel(n_jobs=noJ,
             verbose=3)(delayed(mask_raster_multi)(f[0],
                       mask=f[1]) for f in finalList)
else:
    
    wildCard1 = "*tile*/*tile*/Z_Num"+extraNum+"_DeZoom"+zoomF +"_STD-MALT.tif"
    wildCard2 = "*tile*/*tile*/AutoMask_STD-MALT_Num_"+maskN+".tif"
    
    
    fileListIm = glob(os.path.join(fl, wildCard1))
    fileListMsk = glob(os.path.join(fl, wildCard2))
    
    if len(fileListIm) == 0:
        wildCard1 = "MEC-Malt/Z_Num"+extraNum+"_DeZoom"+zoomF +"_STD-MALT.tif"
        wildCard2 = "MEC-Malt/AutoMask_STD-MALT_Num_"+maskN+".tif"
        fileListIm = glob(os.path.join(fl, wildCard1))
        fileListMsk = glob(os.path.join(fl, wildCard2))
    
    fileListIm.sort()
    fileListMsk.sort()
    
    
    finalList = list(zip(fileListIm, fileListMsk))
    
    Parallel(n_jobs=noJ,
             verbose=3)(delayed(mask_raster_multi)(f[0],
                       mask=f[1]) for f in finalList)






