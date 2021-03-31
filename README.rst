.. -*- mode: rst -*-

Structure from Motion workflows
============

A series of shell and python scripts for Structure from motion processing using the MicMac library. 


**The scripts**

1. Clone/download/unzip this repo to wherever you wish

2. Add the script folders to your path e.g your .bashrc or .bash_profile

.. code-block:: bash
    
    #micmac
    export PATH=/my/path/micmac/bin:$PATH
    
    #sfm scripts
    export PATH=/my/path/Sfm:$PATH
    
    export PATH=/my/path/Sfm/substages:$PATH
    
3. Make them executable

.. code-block:: bash
   
   chmod +x Sfm/*.sh Sfm/*.py Sfm/substages/*.py Sfm/substages/*.sh

4. Update your paths

.. code-block:: bash
    . ~/.bashrc


Dependencies
~~~~~~~~~~~~

Sfm requires:

- GNU/Linux or Mac OS 

- Python 3

- MicMac

- OSSIM


https://micmac.ensg.eu/index.php/Accueil

Dependency installation
~~~~~~~~~~~~~~~~~

**MicMac**

See MicMac install instructions here:

https://micmac.ensg.eu/index.php/Install



For ref only - I don't recommend using GPU-aided processing with MicMac as it appears to be incomplete. 
With reference to GPU supported compilation specifically, the following may help:

- Replace the GpGpu.cmake file with the one supplied here as I have added the later Pascal 6.1 architecture

- Make sure you install and use an older gcc compiler such as 5 or 6 for the cmake bit

- Replace k with no of threads 

.. code-block:: bash
    
    cmake -DWITH_OPEN_MP=OFF
          -DCMAKE_C_COMPILER=/usr/bin/gcc-5
          -DCMAKE_CXX_COMPILER=/usr/bin/g++-5
          -DCUDA_ENABLED=1
          -DCUDA_SDK_ROOT_DIR=/path/to/NVIDIA_CUDA-9.2_Samples/common 
          -DCUDA_SAMPLE_DIR=/path/to/NVIDIA_CUDA-9.2_Samples 
          -DCUDA_CPP11THREAD_NOBOOSTTHREAD=ON ..

    make install -j k

**OSSIM**

Install OSSIM via tha ubuntu GIS or equivalent repo 

- Ensure the OSSIM preferences file is on you path, otherwise it will not recognise different projections

- see here https://trac.osgeo.org/ossim/wiki/ossimPreferenceFile


Contents
~~~~~~~~~~~~~~~~~

All in one scripts
~~~~~~~~~~~~~~~~~~

These process the entire Sfm workflow

**sfm.sh**

- A script to preform the entire SfM workfow producing DSM, Ortho-mosaic & point cloud

**gridproc.sh (DEPRECATED)**

- Process a large dataset (typically 1000s of images+) in tiles 


Sub-stage scripts
~~~~~~~~~~~~~~~~~

These divide the workflow into Orientation, dense cloud/DSM processing and mosaic generation. 
All are internal to the complete workflows.


**Orientation.sh**

- This performs feature detection, relative orientation, orienation with GNSS and sparse cloud generation

- outputs the orientation results as .txt files and the sparse cloud 

**dense_cloud.sh**

- Processes dense cloud using either the PIMs or Malt-based algorithms, ortho-mosaic, point-cloud and georefs everything

**MaltBatch.py**

- This processes data in tiles/chunks using the Malt algorithm, where GPU support is optional

- It is internal to gridproc

**PimsBatch.py**

- This processes data in tiles/chunks using the PIMs algorithm

- this script is an internal option in DronePIMs.sh

**orthomosaic.sh**

- Orthomosaic the output of any of the above including the batch scripts

**MntBatch.py**

- This processes data in tiles/chunks using the PIMs2MNT algorithm

With a big dataset - I have found the Ortho generation fills up the HD with 1000s of images.
Hence, this tiles the ortho generation, assuming you have already globbaly processed the data with PIMs algorithm, and potentially the DSM with PIMs2MNT (without the ortho option).

**MSpec.py**

- This calculates surface reflectance and aligns the offset band imagery for the MicaSense RedEdge and is to be used prior to the usual processing

- Outputs can be either single-band or stacked depending on preference


**MStack.py**

- This uses functionality borrowed from my lib geospatial_learn to stack the 3-band results of processing Micasense red-edge imagery. 
- As MicMac only supports 3-band images, the most efficient solution I currently have is to dense match RGB and RReNir sperately then merge results (more efficient solution to follow!)


**MicMac-LocalChantierDescripteur.xml**
- This is a local descriptor of the camera in the C-Astral Bramor - alter the params for your own camera

The folder ContrastEnhanceChant includes parameters to high pass imagery internally prior to key points (SIFT)

It does not permanently alter the images - but this is possible (look up MicMac docs)

Use
~~~~~~~~~~~~~~~~~

type -h to get help on each script e.g. :

.. code-block:: bash

   Drone.sh -help



Thanks
~~~~~~~~~~~~~~~~~


Thanks to developers and contributors at MicMac and it's forum, particularly L.Girod whose work inspired the basis of the shell scripts and pymicmac from which the tiling function was derived
