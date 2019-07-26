#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 14:45:35 2019

@author: ciaran


SeamMosaic.py -folder PIMs-Ortho -algo Fraser  

Use the micmac teslib seamline mosaicing function - which requires a labourious

image pattern so have used python here 


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

