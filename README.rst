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


Sub-stage scripts
~~~~~~~~~~~~~~~~~

These divide the workflow into Orientation, dense cloud/DSM processing and mosaic generation. 
All are internal to the complete workflows.


**Orientation.sh**

- This performs feature detection, relative orientation, orienation with GNSS and sparse cloud generation

- outputs the orientation results as .txt files and the sparse cloud 

**dense_cloud.sh**

- Processes dense cloud using either the PIMs or Malt-based algorithms, ortho-mosaic, point-cloud and georefs everything

**orthomosaic.sh**

- Orthomosaic the output of any of the above including the batch scripts


Use
~~~~~~~~~~~~~~~~~

type -h to get help on each script e.g. :

.. code-block:: bash

   sfm.sh -help



Thanks
~~~~~~~~~~~~~~~~~


Thanks to developers and contributors at MicMac and it's forum, particularly L.Girod whose work inspired the basis of the shell scripts
