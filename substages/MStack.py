#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 14:28:19 2019

@author: Ciaran Robb

https://github.com/Ciaran1981/Sfm

Funtionality taken from my lib geospatial_learn .geodata module, here for 
self contained script for mutispec data

Usage: typically

MStack.py -in1 RGB/PIMS-ORTHO/Orthophotomosaic.tif -in2 RRENir/PIMS-ORTHO/Orthophotomosaic.tif -o MicasenseStack.tif

"""


# Bloody hell this was a bit hurridly thrown to together
import gdal
from tqdm import tqdm
import argparse

gdal.UseExceptions()

parser = argparse.ArgumentParser()

parser.add_argument("-in1", "--i1", type=str, required=True, 
                    help="first raster")

parser.add_argument("-in2", "--i2", type=str, required=False, 
                    help="second raster")

parser.add_argument("-o", "--oot", type=str, required=False, 
                    help="out raster")
#
#parser.add_argument("-clrcmp", "--cmp", type=str, required=False, 
#                    help="out raster")


args = parser.parse_args() 

def _copy_dataset_config(inDataset, FMT = 'Gtiff', outMap = 'copy',
                         dtype = gdal.GDT_Int32, bands = 1):
    """Copies a dataset without the associated rasters.

    """
#    if FMT == 'HFA':
#        fmt = '.img'
#    if FMT == 'KEA':
#        fmt = '.kea'
#    if FMT == 'Gtiff':
#        fmt = '.tif'
    
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
    
    # Set params for output raster
    outDataset = driver.Create(
        outMap, 
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

def stack_rasters(inRas1, inRas2, outRas, blocksize=256):# clcp=args.cmp):
    
#    if clcp == True:
#        rasterList1 = [2,3]
#        rasterList2 = []
    rasterList1 = [1,2,3]
    rasterList2 = [3, 2]
    
    inDataset1 = gdal.Open(inRas1)
    inDataset2 = gdal.Open(inRas2)
    
    outDataset = _copy_dataset_config(inDataset1, FMT = 'Gtiff', outMap = outRas,
                         dtype = gdal.GDT_Int32, bands = 5)
    
    bnnd = inDataset1.GetRasterBand(1)
    cols = outDataset.RasterXSize
    rows = outDataset.RasterYSize

    # So with most datasets blocksize is a row scanline
    if blocksize == None:
        blocksize = bnnd.GetBlockSize()
        blocksizeX = blocksize[0]
        blocksizeY = blocksize[1]
    else:
        blocksizeX = blocksize
        blocksizeY = blocksize
    del bnnd
    
    
    
    for band in rasterList1:
        bnd1 = inDataset1.GetRasterBand(band)
        ootBnd = outDataset.GetRasterBand(band)
        
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
#                    for band in range(1, bands+1):
                    
                    array = bnd1.ReadAsArray(j, i, numCols, numRows)
    
                    if array is None:
                        continue
                    else:
    
                        ootBnd.WriteArray(array, j, i)
                    
    for k,band in enumerate(rasterList2):
        
        bnd2 = inDataset2.GetRasterBand(band)
        ootBnd = outDataset.GetRasterBand(k+4)
        
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
    #                for band in range(1, bands+1):
                    
                    array = bnd2.ReadAsArray(j, i, numCols, numRows)
                    
                    if array is None:
                        continue
                    else:
    
                        ootBnd.WriteArray(array, j, i)
                        
    outDataset.FlushCache()
    outDataset = None
    
stack_rasters(args.i1, args.i2, args.oot, blocksize=256)    
    