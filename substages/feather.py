#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 14:07:23 2019

@author: ciaran
"""

"""
RadiomImagei = a + b ∗ RadiomImagej
"""


# Seanline feather

# pair of orthoImages
imCpl

# Observations used to adjust the global model of the pair (i,j)
ObsGlob
# Observations used to calculate an average model of equalisation of image i
ObsGlobImi

for each image pair:
    for each block/tile:
        RadiomTileImage = a + b ∗ RadiomTileImagej
        # for the all the radiometric couple observations in a tile
        # how robust is this given all the radiom obs in the tile
        Obs1tile = (a + b ∗ Quartile1(RadiomTileImagej), Quartile1(RadiomTileImagej)
        Obs2tile = (a + b ∗ Quartile3(RadiomTileImagej), Quartile3(RadiomTileImagej)
        Obs1tile + ObsGlobij
        Obs2tile + ObsGlobij
    end for
    RadiomImagei = a + b ∗ RadiomImagej # adjustment of L1 with ObsGlobij
    # Calculation of a model for image pair ij
    Obs1ImCpl = (a + b ∗ Quartile1(RadiomImagej), Quartile1(RadiomImagej)
    Obs2ImCpl = (a + b ∗ Quartile3(RadiomImagej), Quartile3(RadiomImagej)
    
    Obs1ImCpl + ObsGlobImi 
    Obs2ImCpl + ObsGlobImi
end for

for each image do:
    RadiomImagei = a + b ∗ RadiomImagej,k,l,ect ## adjustment of L1 with ObsGlobIm
    # Calculation of an average model for image i
    
    
    