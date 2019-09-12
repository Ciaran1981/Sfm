#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 15:35:40 2019

@author: Ciaran Robb

https://github.com/Ciaran1981/Sfm


A script for processing to surface reflectance and aligning bands on Micasense
Rededge

Based on the material on the micasense lib git site, though this uses the 
micasense lib with multiprocessing disabled as multiprocessing is used in this
scirpt via joblib. 

"""
import os#, sys
import matplotlib.pyplot as plt
#from PIL import Image
#import micasense.metadata as metadata
#import micasense.utils as msutils
#import micasense.plotutils as plotutils
import micasense.imageutils as imageutils
import micasense.capture as capture
#from micasense.panel import Panel
#from micasense.image import Image as MImage
import numpy as np
import micasense.imageset as imageset
from glob2 import glob
import imageio
import argparse
import cv2
#from tqdm import tqdm
from skimage import exposure, util
from subprocess import call#, check_call
from joblib import Parallel, delayed
import gdal#, gdal_array


exiftoolPath=None

helpStk = ("1 = 5 band stack,\n 2 = 2x 3 band images ordered RGB, RedReNir,"
           "\n 2 = 2x 3 band images ordered RGB, RedReNir single thread"
           "\n 2 = 2x 3 band images ordered RGB, RedReNir multi core")

parser = argparse.ArgumentParser()

parser.add_argument("-precal", "--pcal", type=str, required=True, 
                    help="path to pre flight calibration images")

parser.add_argument("-postcal", "--pstcal", type=str, required=False,
                    default=None, help="path to post flight calibration images")

parser.add_argument("-img", "--fimages", type=str, required=True, 
                    help="path to flight images")

parser.add_argument("-o", "--rimages", type=str, required=True, 
                    help="path to output reflectance directory")

parser.add_argument("-alIm", "--alg", type=str, required=True, 
                    help="alignment image")

parser.add_argument("-refBnd", "--rB", type=int, required=False, default=1, 
                    help="band to which others are aligned")

parser.add_argument("-mx", "--mxiter", type=int, required=False, default=100, 
                    help="max iterations in alignment of bands")

parser.add_argument("-nt", "--noT", type=int, required=False, default=-1,
                    help="no of tiles at a time")

parser.add_argument("-stk", "--stack", type=int, required=False, default=None,
                    help=helpStk)

parser.add_argument("-plots", "--plts", type=bool, required=False, default=False,
                    help="whether to plot the alignment")

args = parser.parse_args() 

calibPre = os.path.abspath(args.pcal)

if args.pstcal != None:
    calibPost = os.path.abspath(args.pstcal)


imagesFolder = os.path.abspath(args.fimages)


reflFolder = os.path.abspath(args.rimages)

#nt = args.noT


print("Aligning images, may take a while...")
# Increase max_iterations to 1000+ for better results, but much longer runtimes
'''
Right so each capture means each set of bands 1-5
This requires the image list to be sorted in a way that can be aligned
It appears as though micasense have done this with their lib


'''



# RP03-1731303-SC
#panel_ref = [0.56, 0.56, 0.56, 0.51, 0.55]

# RP03-1731271-SC
panel_ref = [0.55, 0.56, 0.55, 0.50, 0.54]




imgset = imageset.ImageSet.from_directory(imagesFolder)


preCapList = glob(os.path.join(calibPre, "*.tif"))
preCapList.sort()
pCapPre = capture.Capture.from_filelist(preCapList) 
pPreIr = pCapPre.panel_irradiance(panel_ref)

if args.pstcal != None:
    pCapPost = capture.Capture.from_filelist(glob(calibPost, "*.tif")) 

    pPostIr = pCapPost.panel_irradiance(panel_ref)

    panel_irradiance = (pPreIr + pPostIr) / 2
else:
    panel_irradiance = pPreIr
 #RedEdge band_index order

# First we must find an image with decent features from which a band alignment 
# can be applied to the whole dataset
 
wildCrd = "IMG_"+args.alg+"*.tif"
algList = glob(os.path.join(imagesFolder, wildCrd))
#algList.sort()
imAl = capture.Capture.from_filelist(algList) 
imAl.compute_reflectance(panel_irradiance)
#imAl.plot_undistorted_reflectance(panel_irradiance)


rf = args.rB

# func to align and display the result. 
def align_template(imAl, mx, reflFolder, ref_ind=rf):

    
    warp_matrices, alignment_pairs = imageutils.align_capture(imAl,
                                                              ref_index=ref_ind, 
                                                              warp_mode=cv2.MOTION_HOMOGRAPHY,
                                                              max_iterations=mx)
    for x,mat in enumerate(warp_matrices):
        print("Band {}:\n{}".format(x,mat))

    # cropped_dimensions is of the form:
    # (first column with overlapping pixels present in all images, 
    #  first row with overlapping pixels present in all images, 
    #  number of columns with overlapping pixels in all images, 
    #  number of rows with overlapping pixels in all images   )
    dist_coeffs = []
    cam_mats = []
# create lists of the distortion coefficients and camera matricies
    for i,img in enumerate(imAl.images):
        dist_coeffs.append(img.cv2_distortion_coeff())
        cam_mats.append(img.cv2_camera_matrix())
        
    warp_mode = cv2.MOTION_HOMOGRAPHY #alignment_pairs[0]['warp_mode']
    match_index = alignment_pairs[0]['ref_index']
    
    cropped_dimensions, edges = imageutils.find_crop_bounds(imAl, 
                                                            warp_matrices,
                                                            warp_mode=cv2.MOTION_HOMOGRAPHY)
   # capture, warp_matrices, cv2.MOTION_HOMOGRAPHY, cropped_dimensions, None, img_type="reflectance",
    im_aligned = imageutils.aligned_capture(imAl, warp_matrices, warp_mode,
                                            cropped_dimensions, match_index,
                                            img_type="reflectance")
    
    im_display = np.zeros((im_aligned.shape[0],im_aligned.shape[1],5), dtype=np.float32 )
    
    for iM in range(0,im_aligned.shape[2]):
        im_display[:,:,iM] =  imageutils.normalize(im_aligned[:,:,iM])
        
    rgb = im_display[:,:,[2,1,0]] 
    cir = im_display[:,:,[3,2,1]] 
    grRE = im_display[:,:,[4,2,1]] 
    
    
    if args.plts == True:
        
        fig, axes = plt.subplots(1, 3, figsize=(16,16)) 
        plt.title("Red-Green-Blue Composite") 
        axes[0].imshow(rgb) 
        plt.title("Color Infrared (CIR) Composite") 
        axes[1].imshow(cir) 
        plt.title("Red edge-Green-Red (ReGR) Composite") 
        axes[2].imshow(grRE) 
        plt.show()
    
    prevList = [rgb, cir, grRE]
    nmList = ['rgb.jpg', 'cir.jpg', 'grRE.jpg']
    names = [os.path.join(reflFolder, pv) for pv in nmList]
    
    for ind, p in enumerate(prevList):
        #img8 = bytescale(p)
        imgre = exposure.rescale_intensity(p)
        img8 = util.img_as_ubyte(imgre)
        imageio.imwrite(names[ind], img8)
    
    return warp_matrices, alignment_pairs#, dist_coeffs, cam_mats, cropped_dimensions

warp_matrices, alignment_pairs = align_template(imAl, args.mxiter,reflFolder,
                                                ref_ind=rf)

    
# prep work dir


# Main func to  write bands to their respective directory

def proc_imgs(i, warp_matrices, bndFolders, panel_irradiance, normalize=None):
    
    
#    for i in imgset.captures: 
    
    i.compute_reflectance(panel_irradiance) 
    #i.plot_undistorted_reflectance(panel_irradiance)  


    cropped_dimensions, edges = imageutils.find_crop_bounds(i, warp_matrices)
    
    im_aligned = imageutils.aligned_capture(i, warp_matrices,
                                            cv2.MOTION_HOMOGRAPHY,
                                            cropped_dimensions,
                                            None, img_type="reflectance")
    
    im_display = np.zeros((im_aligned.shape[0],im_aligned.shape[1],5), dtype=np.float32 )
    
    for iM in range(0,im_aligned.shape[2]):
        im_display[:,:,iM] =  imageutils.normalize(im_aligned[:,:,iM])*65535
    
    for k in range(0,im_display.shape[2]):
         im = i.images[k]
         hd, nm = os.path.split(im.path)
         outdata = im_aligned[:,:,i]
         outdata[outdata<0] = 0
         outdata[outdata>1] = 1
         
         outfile = os.path.join(bndFolders[k], nm)
         imageio.imwrite(outfile, outdata)
        
         cmd = ["exiftool", "-tagsFromFile", im.path,  "-file:all", "-iptc:all",
               "-exif:all",  "-xmp", "-Composite:all", outfile, 
               "-overwrite_original"]
         call(cmd)

def proc_imgs_comp(i, warp_matrices, bndFolders, panel_irradiance):
    
    
    
    i.compute_reflectance(panel_irradiance) 
    #i.plot_undistorted_reflectance(panel_irradiance)  


    cropped_dimensions, edges = imageutils.find_crop_bounds(i, warp_matrices)
    
    im_aligned = imageutils.aligned_capture(i, warp_matrices,
                                            cv2.MOTION_HOMOGRAPHY,
                                            cropped_dimensions,
                                            None, img_type="reflectance")
    
    im_display = np.zeros((im_aligned.shape[0],im_aligned.shape[1],5), dtype=np.float32 )
    
    for iM in range(0,im_aligned.shape[2]):
        im_display[:,:,iM] =  imageutils.normalize(im_aligned[:,:,iM])
    
    rgb = im_display[:,:,[2,1,0]] 
    #cir = im_display[:,:,[3,2,1]] 
    RRENir = im_display[:,:,[4,3,2]] 
    
    imoot = [rgb, RRENir]
    imtags = ["RGB.tif", "RRENir.tif"]
    im = i.images[1]
    hd, nm = os.path.split(im.path[:-5])
    
    for ind, k in enumerate(bndFolders):
         
         #img8 = bytescale(imoot[ind])
         imgre = exposure.rescale_intensity(imoot[ind])
         img8 = util.img_as_ubyte(imgre)
         outfile = os.path.join(k, nm+imtags[ind])
         
         imageio.imwrite(outfile, img8)
        
         cmd = ["exiftool", "-tagsFromFile", im.path,  "-file:all", "-iptc:all",
               "-exif:all",  "-xmp", "-Composite:all", outfile, 
               "-overwrite_original"]
         call(cmd)
# for ref
#[proc_imgs(imCap, warp_matrices, reflFolder) for imCap in imgset]
def proc_stack(i, warp_matrices, bndFolders, panel_irradiance):
    
    i.compute_reflectance(panel_irradiance) 
        #i.plot_undistorted_reflectance(panel_irradiance)  
    
    
    cropped_dimensions, edges = imageutils.find_crop_bounds(i, warp_matrices)
    
    im_aligned = imageutils.aligned_capture(i, warp_matrices,
                                            cv2.MOTION_HOMOGRAPHY,
                                            cropped_dimensions,
                                            None, img_type="reflectance")
    
    im_display = np.zeros((im_aligned.shape[0],im_aligned.shape[1],5), 
                          dtype=np.float32)
    
    rows, cols, bands = im_display.shape
    driver = gdal.GetDriverByName('GTiff')
    
    im = i.images[1].path
    hd, nm = os.path.split(im[:-6])

    filename = os.path.join(reflFolder, nm+'.tif') #blue,green,red,nir,redEdge
    #
    
    outRaster = driver.Create(filename, cols, rows, 5, gdal.GDT_Byte)
    normalize = False
    
    # Output a 'stack' in the same band order as RedEdge/Alutm
    # Blue,Green,Red,NIR,RedEdge[,Thermal]
    
    # NOTE: NIR and RedEdge are not in wavelength order!
    
    i.compute_reflectance(panel_irradiance+[0])
    
    for i in range(0,5):
        outband = outRaster.GetRasterBand(i+1)
        if normalize:
            outband.WriteArray(imageutils.normalize(im_aligned[:,:,i])*65535)
        else:
            outdata = im_aligned[:,:,i]
            outdata[outdata<0] = 0
            outdata[outdata>1] = 1
            
            outband.WriteArray(outdata*65535)
        outband.FlushCache()
    
    if im_aligned.shape[2] == 6:
        outband = outRaster.GetRasterBand(6)
        outdata = im_aligned[:,:,5] * 100 # scale to centi-C to fit into uint16
        outdata[outdata<0] = 0
        outdata[outdata>65535] = 65535
        outband.WriteArray(outdata)
        outband.FlushCache()
    outRaster = None
    
    cmd = ["exiftool", "-tagsFromFile", im,  "-file:all", "-iptc:all",
               "-exif:all",  "-xmp", "-Composite:all", filename, 
               "-overwrite_original"]
    call(cmd)
            

         
if args.stack != None:
    
    if args.stack == 1:
        print("Producing pairs of 3-band composites single thread")
        bndNames = ['RGB', 'RRENir']
        bndFolders = [os.path.join(reflFolder, b) for b in bndNames]
        [os.mkdir(bf) for bf in bndFolders]
        [proc_imgs_comp(imCap, warp_matrices, bndFolders, panel_irradiance) for imCap in imgset.captures]
    
    if args.stack == 2:
        print("Producing 5-band composites")
        bndNames = ['B', 'G', 'R', 'NIR', 'RE' ]
        bndFolders = [os.path.join(reflFolder, b) for b in bndNames]
        [os.mkdir(bf) for bf in bndFolders]
    
        [proc_stack(imCap ,warp_matrices,
                    panel_irradiance) for imCap in imgset.captures]
        
    elif args.stack == 3:
        print("Producing pairs of 3-band composites muti core")
        #prep the dir
        bndNames = ['RGB', 'RRENir']
        bndFolders = [os.path.join(reflFolder, b) for b in bndNames]
        [os.mkdir(bf) for bf in bndFolders]
        
        Parallel(n_jobs=args.noT,
                 verbose=2)(delayed(proc_imgs_comp)(imCap, warp_matrices,
                           bndFolders,
                           panel_irradiance) for imCap in imgset.captures)
        

else:
    print("Producing single band images")
    
    bndNames = ['Blue', 'Green', 'Red', 'NIR', 'Red edge']
    bndFolders = [os.path.join(reflFolder, b) for b in bndNames]
    [os.mkdir(bf) for bf in bndFolders]
    Parallel(n_jobs=args.noT,
             verbose=2)(delayed(proc_imgs)(imCap,
             warp_matrices,
             bndFolders,
             panel_irradiance) for imCap in imgset.captures)
    
    

    