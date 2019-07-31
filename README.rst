.. -*- mode: rst -*-

Structure from Motion workflows
============

A series of python and shell scripts for processing data from drones, originally for the the C-Astral Bramour PPX platform, but will work with most imagery.

Installation
~~~~~~~~~~~~~~~~~


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

**QGIS plugin**

To enable use of MicMac and scripts for those who fear the command line...

This is just a front-end for the native MicMac QT menus at present. The scaled versions that utilise the script functionality are not done as yet, but will be added in due course. 

NOT FINISHED!!! Please wait until I upload to the repo.....

(Unles you wish to manually paste it into your plugin folder and alter the mm3d variable to your own micmac bin path)


Dependencies
~~~~~~~~~~~~

Sfm requires:

- GNU/Linux or Mac OS for full functionality (python scripts are not platform dependent)

- Python 3

- MicMac

- OSSIM


https://micmac.ensg.eu/index.php/Accueil

Dependency installation
~~~~~~~~~~~~~~~~~

**MicMac**

See MicMac install instructions here:

https://micmac.ensg.eu/index.php/Install

If you have a lot of CPU cores, it is almost always better not to bother with GPU aided processing on MicMac in its current state as with lots of jobs/images it will overload the GPU memory.

The only case in which I have found GPU processing to be any use is with my MaltBatch.py script - but you have to manage the no of CPU cores and watch image size/numbers.

If you have relatively few CPU cores, then GPU accerallation is probably more meritful.  

- I have found it is best to install MicMac wthout the GPU as my main install and add it to the path 

- Then I install a separate micmac with GPU support and add it as a variable in shell scripts or the absoulute path when needed

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

**micasense**

cd into the micasense folder and type 

.. code-block:: python

    python setup.py install
    
You will then see the instructions but anyway - activate when using the multspec scripts

.. code-block:: bash

    conda activate micasense_Sfm
or

.. code-block:: bash

    source activate micasense_Sfm
    
This is my own fork of micasense but only has a couple of lines changed as well as getting its dependencies from the official conda


Contents
~~~~~~~~~~~~~~~~~

All in one scripts
~~~~~~~~~~~~~~~~~~

These process the entire Sfm workflow

**Drone.sh**

- A script to process photographs with complete exif information outputting orthomosaic, DSM and point cloud (.ply) file
Typically a DJI phantom or other such platform. This uses Malt for dense matching

**DronePIMs.sh**

- A script like the previous but using the PIMs algorithm


**gridproc.sh**

- Process a large dataset (typically 100s-1000s of images) in tiles (this appears to be best for large ortho-mosaics)


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

Thanks to devs and contributors at MicMac and it's forum, particularly L.Girod whose work inspired the basis of the shell scripts and pymicmac from which the tiling function was derived
