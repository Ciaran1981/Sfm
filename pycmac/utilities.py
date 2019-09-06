#!/home/ciaran/anaconda3/bin/python
# -*- coding: utf-8 -*-
"""
Created on Tue May 29 16:20:58 2018

@author: ciaran

calib_subset.py -folder mydir -algo Fraser  -csv mycsv.csv

"""

import numpy as np
import pandas as pd
import os

import glob2

from joblib import Parallel, delayed
import lxml.etree
import lxml.builder    
from os import path
from shutil import copy
from subprocess import call
import gdal
from tqdm import tqdm
import ogr

from sklearn import metrics


def calib_subset(folder, csv, ext="JPG",  algo="Fraser"):
    
    """
    
    A function for calibrating on an image subset then initialising a global
    orientation 
            
    Notes
    -----------
    
    Purely for convenience within python - not really necessary - 
    
    
    see MicMac tools link for further possible kwargs - just put the module cmd as a kwarg
    
    
    
        
    Parameters
    -----------
    
    folder : string
           working directory
    proj : string
           a UTM zone eg "30 +north" 
        
    mode : string
             Correlation mode - Ortho, UrbanMNE, GeomImage
        
    ext : string
                 image extention e.g JPG, tif
    
    orientation : string
                 orientation folder to use (generated by previous tools/cmds)
                 default is "Ground_UTM"
    
       
    """

    
    
    dF = pd.read_table(csv)
    
    imList = list(dF['#F=N'])
    imList.sort()
    
    
    #subList = [path.split(item)[1] for item in imList]
    
    subStr = str(imList)
    
    sub2 = subStr.replace("[", "")
    sub2 = sub2.replace("]", "")
    sub2 = sub2.replace("'", "") 
    sub2 = sub2.replace(", ", "|")                 
    
    mm3d = ["mm3d", "Tapas", algo, sub2,  "Out=Calib", "SH=_mini"]
    
    mm3dFinal = ["mm3d", "Tapas", algo, ".*"+ext, "Out=Arbitrary", 
                 "InCal=Calib", "SH=_mini"]
    
    call(mm3d)
    
    call(mm3dFinal)
    
def convert_c3p(folder, lognm, ext="JPG", mspec=False):
    
    """
    Edit csv file for c3p to work with MicMac.
    
    This is intended for the output from the software of a C-Astral drone
    
    This assumes the column order is name, x, y, z
    
    Parameters
    ----------  
    
    folder : string
            path to folder containing jpegs
    lognm : string
            path to c3p derived csv file
    ext : string
            image extension
    ms : bool
            If using multispec 2 csvs will be produced, with the file prefixes for the MSpec outputs
                           
    """
    # Get a list of file paths 
    fileList = glob2.glob(os.path.join(folder, "*."+ext))
    
    #split them so it is just the jpg (ugly yes)
    # these will constitute the first column of the output csv
    files = [os.path.split(file)[1] for file in fileList]
    files.sort()
    

    
    fileF = [files[k] for k in range(0, len(files), 5)]

    # must be read as an object as we are dealing with strings and numbers
    #npCsv = np.loadtxt(lognm, dtype='object')
    
    def _mmlog(lognm, outlog, postxt=None):
        
        with open(lognm, 'r') as f:
            header = f.readline().strip('\n').split(';')
            x_col = header.index('Longitude')
            y_col = header.index('Latitude')
            z_col = header.index('Altitude')
            x = []
            y = []
            z = []
            
            for line in f:
                l = line.strip('\n').split(';')
                
                x.append(l[x_col])
                y.append(l[y_col])
                z.append(l[z_col])
        
        if postxt == None:
            with open(outlog, "w") as oot:
                oot.write("#F=N X Y Z \n")
                for idx, vr in enumerate(fileF):
                    flnm = vr
                    s = ' '
                    outStr = s.join([flnm, x[idx], y[idx], z[idx], "\n"])
                    oot.write(outStr)
        else:
            with open(outlog, "w") as oot:
                oot.write("#F=N X Y Z \n")
                for idx, vr in enumerate(fileF):
                    flnm = vr[:-5]+postxt
                    s = ' '
                    outStr = s.join([flnm, x[idx], y[idx], z[idx], "\n"])
                    oot.write(outStr)
                
    rgblog = lognm[:-4]+'_rgb.csv'
    cirlog = lognm[:-4]+'_renir.csv'         
        
    if mspec == True:
                               
        _mmlog(lognm, rgblog, postxt="RGB.tif")
        _mmlog(lognm, cirlog, postxt="RRENir.tif")        
    else:
        _mmlog(lognm, rgblog)
        
        
                                         


def mv_subset(csv, inFolder, outfolder):
    
    """
    Move a subset of images based on a MicMac csv file
    
    Parameters
    ----------  
    
    folder : string
            path to folder containing jpegs
    lognm : string
            path to c3p derived csv file
                           
    """
    
    os.chdir(inFolder)
    
    dF = pd.read_table(csv)
    
    dfList = list(dF['#F=N'])
    
    Parallel(n_jobs=-1,verbose=5)(delayed(copy)(file, 
            outfolder) for file in dfList)
    
def make_xml(csvFile, folder, yaw=None):
    
    """
    Make an xml based for the rtl system in micmac
    
    Parameters
    ----------  
    
    csvFile : string
             csv file with coords to use
    """
    
    # I detest xml writing!!!!!!!!!!!!!!!
    E = lxml.builder.ElementMaker()
    
    root = E.SystemeCoord
    doc = E.BSC
    f1 = E.TypeCoord
    f2 = E.AuxR
    f3 = E.AuxRUnite

    
    csv = pd.read_table(csvFile)#, delimiter=" ")
#    if len(csv.columns) == 1:
#        csv = pd.read_table(csvFile, delimiter=" ")
        
    x = str(csv.X[0])
    y = str(csv.Y[0])
    z = str(csv.Z[0])
    
    # if we are including yaw pitch and roll (k,w,p)
    if yaw != None:            
        k = str(csv.K[0])
        w = str(csv.W[0])
        p = str(csv.Z[0])          
    # Bloody hell this is better than etree at least       
        xmlDoc = (root(doc(f1('eTC_RTL'),f2(x),
                           f2(y),
                           f2(z), 
                           f2(k),
                           f2(w),
                           f2(p),),
                doc(f1('eTC_WGS84'),
                               f3('eUniteAngleDegre'))))
    else:
        xmlDoc = (root(doc(f1('eTC_RTL'),f2(x),
                       f2(y),
                       f2(z),), 
            doc(f1('eTC_WGS84'),
                           f3('eUniteAngleDegre'))))
    
    et = lxml.etree.ElementTree(xmlDoc)
    ootXml = path.join(folder, 'SysCoRTL.xml')
    et.write(ootXml, pretty_print=True)

def make_sys_utm(folder, proj):
    
    E = lxml.builder.ElementMaker()
    
    root = E.SystemeCoord
    doc = E.BSC
    f1 = E.TypeCoord
    f2 = E.AuxR
    f3 = E.AuxStr
    

    xmlDoc = (root(doc(f1('eTC_Proj4'),
                   f2('1'),
                   f2('1'), 
                   f2('1'),
                   f3(proj))))
    et = lxml.etree.ElementTree(xmlDoc)
    
    ootXml = path.join(folder,'SysUTM.xml')
    et.write(ootXml, pretty_print=True)
    
    
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
              the input raster 
        
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
                    array = np.zeros(shape=(numRows,numCols))
                    for band in range(1, bands+1):
                        bnd = inDataset.GetRasterBand(band)
                        array = bnd.ReadAsArray(j, i, numCols, numRows)
                        array[mask != mval]=0
                        array[array < 0]=0
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
 
def num_subset(inFolder, outFolder, num=5, ext="JPG"):
    
    """ 
    Pick a subset of images from a video such as every fifth image (frame)
    
    
    Parameters 
    ----------- 
    
    inFolder : string
              the input raster 
        
    outFolder : string
           the masking value that delineates pixels to be kept
        
    num : int 
              the subdivision - e.g. every fifth image

    ext : string
                 image extention e.g JPG, tif
        

    """
    # ffmpeg cmd just in case I end up[ doing anything like this]
    # ffmpeg -i *.mp4 Im_0000_%5d_Ok.png
    
    fileList = glob2.glob(os.path.join(inFolder, "*."+ext))
        
    
    
#    files = [os.path.split(file)[1] for file in fileList]
#    files.sort()
    
    ootList = []
    
    for f in range(0, len(fileList), num):
        ootList.append(fileList[f])
        
        
    
    Parallel(n_jobs=-1,verbose=5)(delayed(copy)(fl, 
            outFolder) for fl in ootList)


def rmse_vector_lyr(inShape, attributes):

    """ 
    Using sklearn get the rmse of 2 vector attributes 
    (the actual and predicted of course in the order ['actual', 'pred'])
    
    
    Parameters 
    ----------- 
    
    inShape : string
              the input vector of OGR type
        
    attributes : list
           a list of strings denoting the attributes
         

    """    
    
    #open the layer etc
    shp = ogr.Open(inShape)
    lyr = shp.GetLayer()
    labels = np.arange(lyr.GetFeatureCount())
    
    # empty arrays for att
    pred = np.zeros((1, lyr.GetFeatureCount()))
    true = np.zeros((1, lyr.GetFeatureCount()))
    
    for label in labels: 
        feat = lyr.GetFeature(label)
        true[:,label] = feat.GetField(attributes[0])
        pred[:,label] = feat.GetField(attributes[1])
    
    
    
    error = np.sqrt(metrics.mean_squared_error(true, pred))
    
    return error
    
        
    
    



       