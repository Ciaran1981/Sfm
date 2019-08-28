#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 14:45:37 2019

@author: ciaran


I wrote this as a blade of grass got stuck in the drone camera lens

So had to crop everything


"""

#from PIL import  Image
from glob2 import glob
from os import path, mkdir
import argparse
from subprocess import call
from joblib import Parallel, delayed
from shutil import rmtree
from skimage.io import imread#, imsave
from skimage.util import crop, img_as_ubyte
from skimage .exposure import rescale_intensity

import imageio

parser = argparse.ArgumentParser()

parser.add_argument("-fld", "--inF", type=str, required=True, 
                    help="path to folder of images to be cropped")

parser.add_argument("-o", "--oot", type=str, required=True,
                     help="path to folder for cropped images")

parser.add_argument("-nt", "--noT", type=int, required=False, default=-1,
                    help="no of threads at a time")

parser.add_argument("-cr", "--crp", type=int, required=False, default=120,
                    help="crop ")

args = parser.parse_args() 

imList = glob(path.join(path.abspath(args.inF), '*.tif'))

outFolder = args.oot

thrd = args.noT

cropp = args.crp

if path.exists(outFolder):
    rmtree(outFolder)

mkdir(outFolder)

def clipper(i, outFolder):

#for i in imList:
    hd, tl = path.split(i)
    im = imread(i)
    cropped = crop(im, ((cropp, 0), (0, 0), (0, 0)), copy=False)
    imgre = rescale_intensity(cropped)
    img8 = img_as_ubyte(imgre)

#    cropped =im.crop((120, 0, 1227, 909))
    outFile = path.join(outFolder, tl)
#    cropped.save(outFile)
    imageio.imwrite(outFile, img8)

    cmd = ["exiftool", "-tagsFromFile", i,  "-file:all", "-iptc:all",
           "-exif:all",  "-xmp", "-Composite:all", outFile, 
           "-overwrite_original"]
    call(cmd)

if thrd == 1:
    [clipper(img, outFolder) for img in imList]
else:
    Parallel(n_jobs=thrd, verbose=2)(delayed(clipper)(img, 
            outFolder) for img in imList)    

# load exif data

