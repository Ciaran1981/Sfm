#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 15:06:06 2018

@author: ciaran

A script to create an relative coord system from the first entry in a csv


"""

import pandas as pd
import lxml.etree
import lxml.builder    
import argparse 
import os

parser = argparse.ArgumentParser()

parser.add_argument("-csv", "--cs", type=str, required=True, 
                    help="input csv")

parser.add_argument("-d", "--delim", type=str, required=False, default=None, 
                    help="delimeter for csv")
parser.add_argument("-kwp", "--ypr", type=str, required=False, default=None, 
                    help="inclusion of yaw pitch roll - not required")

args = parser.parse_args()


def make_xml(csvFile, folder, sep=" "):
    
    """
    Make an xml  for the rtl system in micmac
    
    Parameters
    ----------  
    
    csvFile : string
             csv file with coords to use
    """
    
    # wee xml for mm3d to manipulate coords
    E = lxml.builder.ElementMaker()
    
    root = E.SystemeCoord
    doc = E.BSC
    f1 = E.TypeCoord
    f2 = E.AuxR
    f3 = E.AuxRUnite
    
    csv = pd.read_csv(csvFile, sep=sep)
                
    x = str(csv.X[0])
    y = str(csv.Y[0])
    z = str(csv.Z[0])


    xmlDoc = (root(doc(f1('eTC_RTL'),f2(x),
                   f2(y),
                   f2(z),), 
        doc(f1('eTC_WGS84'),
                       f3('eUniteAngleDegre'))))
    
    et = lxml.etree.ElementTree(xmlDoc)
    ootXml = os.path.join(folder, 'SysCoRTL.xml')
    et.write(ootXml, pretty_print=True)



cwd = os.getcwd()

make_xml(args.cs, cwd)



