#!/usr/bin/python
"""
# Author Ciaran Robb
# Aberystwyth University

https://github.com/Ciaran1981/Sfm

This ia a cut down adaptation of a script from the pymicmac lib - credit to those folks for doing that

It produces lists of images per tile that are them processed by either
PimsBatch.py or MaltBatch.py depending on preference. 

"""


import os
import glob
import numpy
from lxml import etree
from scipy import spatial


def getTileIndex(pX, pY, minX, minY, maxX, maxY, nX, nY):
    xpos = int((pX - minX) * nX / (maxX - minX))
    ypos = int((pY - minY) * nY / (maxY - minY))
    # If it is in the edge of the box (in the maximum side) we need to put in
    # the last tile
    if xpos == nX:
        xpos -= 1
    if ypos == nY:
        ypos -= 1
    return (xpos, ypos)


def run(orientationFolder, homolFolder, imagesFormat,
        numNeighbours, outputFolder, num, overLap=10):

    if not os.path.isdir(orientationFolder):
        raise Exception(orientationFolder + ' does not exist')
    includeHomol = homolFolder != ''
    if includeHomol and not os.path.isdir(homolFolder):
        raise Exception(homolFolder + ' does not exist')

    os.makedirs(outputFolder)

    mmLocalChanDescFile = 'MicMac-LocalChantierDescripteur.xml'
    requireLocalChanDescFile = ''
    if os.path.isfile(mmLocalChanDescFile):
        requireLocalChanDescFile = mmLocalChanDescFile

    # Parse number of tiles in X and Y
    nX, nY = [int(e) for e in num.split(',')]

    # Initialize the empty lists of images and 2D points with the x,y
    # positions of the cameras
    images = []
    camera2DPoints = []

    # For each image we get the x,y position of the camera and we add the
    # image and th epoint in the lists
    orientationFiles = glob.glob(orientationFolder + '/Orientation*')
    for orientationFile in orientationFiles:
        images.append(
            os.path.basename(orientationFile).replace(
                "Orientation-",
                "").replace(
                ".xml",
                ""))
        e = etree.parse(orientationFile).getroot()
        (x, y, _) = [float(c)
                     for c in e.xpath("//Externe")[0].find('Centre').text.split()]
        camera2DPoints.append((x, y))

    if numNeighbours >= len(images):
        raise Exception("numNeighbours >= len(images)")

    # Compute the bounding box of all the camera2DPoints
    minX, minY = numpy.min(camera2DPoints, axis=0)
    maxX, maxY = numpy.max(camera2DPoints, axis=0)

    print("Bounding box: " + ','.join([str(e)
                                       for e in [minX, minY, maxX, maxY]]))
    print("Offset bounding box: " +
          ','.join([str(e) for e in [0, 0, maxX - minX, maxY - minY]]))

    # Compute the size of the tiles in X and Y
    tileSizeX = (maxX - minX) / nX
    tileSizeY = (maxY - minY) / nY

    # Create a KDTree to query nearest neighbours
    kdtree = spatial.KDTree(camera2DPoints)

    # Check that tiles are small enough with the given images
    numSamplePoints = 100
    distances = []
    for camera2DPoint in camera2DPoints[:numSamplePoints]:
        distances.append(kdtree.query(camera2DPoint, 2)[0][1])

    # For each tile first we get a list of images whose camera XY position lays within the tile
    # note: there may be empty tiles
    tilesImages = {}
    for i, camera2DPoint in enumerate(camera2DPoints):
        pX, pY = camera2DPoint
        tileIndex = getTileIndex(pX, pY, minX, minY, maxX, maxY, nX, nY)
        if tileIndex not in tilesImages:
            tilesImages[tileIndex] = [images[i], ]
        else:
            tilesImages[tileIndex].append(images[i])

    # Create output file
    # For each tile we extend the tilesImages list with the nearest neighbours
    count=0
    for i in range(nX):
        for j in range(nY):
            count +=1
            k = (i, j)
            (tMinX, tMinY) = (minX + (i * tileSizeX), minY + (j * tileSizeY))
            (tMaxX, tMaxY) = (tMinX + tileSizeX, tMinY + tileSizeY)
            tCenterX = tMinX + ((tMaxX - tMinX) / 2.)
            tCenterY = tMinY + ((tMaxY - tMinY) / 2.)
            if k in tilesImages:
                imagesTile = tilesImages[k]
            else:
                imagesTile = []
            imagesTileSet = set(imagesTile)

            imagesTileSet.update([images[nni] for nni in kdtree.query(
                (tCenterX, tCenterY), numNeighbours)[1]])
            imagesTileSet.update(
                [images[nni] for nni in kdtree.query((tMinX, tMinY), numNeighbours)[1]])
            imagesTileSet.update(
                [images[nni] for nni in kdtree.query((tMinX, tMaxY), numNeighbours)[1]])
            imagesTileSet.update(
                [images[nni] for nni in kdtree.query((tMaxX, tMinY), numNeighbours)[1]])
            imagesTileSet.update(
                [images[nni] for nni in kdtree.query((tMaxX, tMaxY), numNeighbours)[1]])

            if includeHomol:
                imagesTileSetFinal = imagesTileSet.copy()
                # Add to the images for this tile, othe rimages that have
                # tie-points with the current images in the tile
                for image in imagesTileSet:
                    imagesTileSetFinal.update(
                        [e.replace('.dat', '') for e in os.listdir(homolFolder + '/Pastis' + image)])
                imagesTileSet = imagesTileSetFinal

            if len(imagesTileSet) == 0:
                raise Exception('EMPTY TILE!')

            tileName = 'tile_' + str(i) + '_' + str(j)

            tMaxY = int(tMaxY) + overLap
            tMaxX = int(tMaxX) + overLap
                
            # Here is the bounding box in a very ugly expression from pymicmac orig
            box = "BoxTerrain=[" + ",".join([str(e) for e in (tMinX, tMinY, tMaxX, tMaxY)]) + "]"
            # Dump the list of images for this tile
            tileImageListOutputFileName = outputFolder + '/' + tileName + '.list'
            
            
            tileImageListOutputFile = open(tileImageListOutputFileName, 'w')
            
            tileImageListOutputFile.write(box+'\n')
            
            tileImageListOutputFile.write('\n'.join(sorted(imagesTileSet)))
            tileImageListOutputFile.close()
            # Should this be added to give the option if feathering can be made to work
            




