
#Created on Fri May  3 17:23:41 2019

#https://github.com/Ciaran1981/Sfm

#A shell script to process the dense cloud only using the PIMs algorithm

#Purely for convenience

#Usage dense_cloud.sh -e JPG -a Forest -m PIMs -u 30 +north -z 4 -r 0.02



while getopts ":e:a:m:u:z:d:n:r:o:h:" o; do
  case ${o} in
    h) 
      echo "Process dense cloud using either PIMs or Malt."
      echo "Usage: dense_cloud.sh -e JPG -a Forest -m PIMs -z 4 -r 0.02"
      echo "-e EXTENSION     : image file type (JPG, jpg, TIF, png..., default=JPG)."
      echo "-a Algorithm     : type of algo eg BigMac, MicMac, Forest, Statue etc"
      echo "-m MODE          : Either Malt or PIMs - mandatory"
      echo "-u UTMZONE       : UTM Zone of area of interest. Takes form 'NN +north(south)'"
      echo "-z ZoomF         : Last step in pyramidal dense correlation (default=2, can be in [8,4,2,1])"
      echo "-d DEQ           : Degree of equalisation between images during mosaicing (See mm3d Tawny)"
      echo "-n CORE          : Number of cores to use - likely best to stick with physical ones"
      echo "-r               : zreg term - context dependent "     
      echo "-o               : do ortho -True or False "           
      echo "-h	             : displays this message and exits."
      echo " "
      exit 0 
      ;;    
	e)   
      EXTENSION=${OPTARG} 
      ;;
    a)
      Algorithm=${OPTARG}
      ;;
    m)
      MODE=${OPTARG}
      ;;
	u)
      UTM=${OPTARG}
      ;;
	z)
      ZoomF=${OPTARG}
      ;;
	d)
      DEQ=${OPTARG}  
      ;;
	n)
      CORE=${OPTARG}  
      ;;  
    r)
      zreg=${OPTARG}
      ;;
    o)
      orth=${OPTARG}
      ;;
    \?)
      echo "dense_cloud.sh: Invalid option: -${OPTARG}" >&1
      exit 1
      ;;
    :)
      echo "dense_cloud.sh: Option -${OPTARG} requires an argument." >&1
      exit 1
      ;;
  esac
done

shift $((OPTIND-1))
 
mkdir OUTPUT

if [[ "$MODE" = "PIMs" ]]; then
    echo "Using PIMs Algorithm"
    mm3d PIMs $Algorithm .*${EXTENSION} Ground_UTM DefCor=0 ZoomF=$ZoomF ZReg=$zreg  
    
    
    if  [ -n "${orth}" ]; then
        echo "Doing ortho imagery"
        mm3d PIMs2MNT $Algorithm DoMnt=1 DoOrtho=1
    
        mm3d Tawny PIMs-ORTHO/ RadiomEgal=0 Out=Orthophotomosaic.tif
       
    
        mm3d ConvertIm PIMs-ORTHO/Orthophotomosaic.tif Out=OUTPUT/OrthFinal.tif
        cp PIMs-ORTHO/Orthophotomosaic.tfw OUTPUT/OrthFinal.tfw
        gdal_edit.py -a_srs "+proj=utm +zone=$UTM +ellps=WGS84 +datum=WGS84 +units=m +no_defs" OUTPUT/OrthFinal.tif
        mm3d Nuage2Ply PIMs-TmpBasc/PIMs-Merged.xml Attr=PIMs-ORTHO/Orthophotomosaic.tif Out=OUTPUT/pointcloud.ply
    else
        echo "Doing DSM only"
        mm3d PIMs2MNT $Algorithm DoMnt=1 
        mm3d PIMs2PLY $Algorithm Out=OUTPUT/pointcloud.ply
    fi
    
    mask_dsm.py -folder $PWD -pims 1
    
    mm3d GrShade PIMs-TmpBasc/PIMs-Merged_Prof.tif ModeOmbre=IgnE Out=OUTPUT/Shade.tif
    
    
    cp PIMs-TmpBasc/PIMs-Merged_Prof.tfw OUTPUT/DSM.tfw
    cp PIMs-TmpBasc/PIMs-Merged_Prof.tif OUTPUT/DSM.tif
    cp PIMs-TmpBasc/PIMs-Merged_Masq.tif OUTPUT/Mask.tif
    cp PIMs-TmpBasc/PIMs-Merged_Prof.tfw OUTPUT/Mask.tfw
    cp PIMs-TmpBasc/PIMs-Merged_Prof.tfw OUTPUT/Corr.tfw
    cp PIMs-TmpBasc/PIMs-Merged_Correl.tif OUTPUT/Corr.tif
    
    gdal_edit.py -a_srs "+proj=utm +zone=${UTM}  +ellps=WGS84 +datum=WGS84 +units=m +no_defs" DSM.tif
    gdal_edit.py -a_srs "+proj=utm +zone=${UTM}  +ellps=WGS84 +datum=WGS84 +units=m +no_defs" Mask.tif
    gdal_edit.py -a_srs "+proj=utm +zone=${UTM}  +ellps=WGS84 +datum=WGS84 +units=m +no_defs" Corr.tif   
    
else
    echo "Using Malt Algorithm"
    # Here we find the physical CPU count to avoid thread errors in cmake
    CpuCount=($(lscpu -p | egrep -v '^#' | sort -u -t, -k 2,4 | wc -l))
    
    if  [ -n "${orth}" ]; then
    	mm3d Malt $Algorithm ".*.${EXTENSION}" Ground_UTM UseGpu=0 EZA=1 DoOrtho=1 DefCor=0 #NbProc=$CpuCount
    else
        mm3d Malt $Algorithm ".*.${EXTENSION}" Ground_UTM UseGpu=0 EZA=1 DoOrtho=1 DefCor=0 #NbProc=$CpuCount
    
        mm3d Tawny Ortho-MEC-Malt RadiomEgal=0 
        #mm3d Nuage2Ply MEC-Malt/NuageImProf_STD-MALT_Etape_8.xml Attr=Ortho-MEC-Malt/Orthophotomosaic.tif Out=OUTPUT/PointCloud_OffsetUTM.ply Offs=[${X_OFF},${Y_OFF},0]
    fi
    
     

    #PointCloud from Ortho+DEM, with offset substracted to the coordinates to solve the 32bit precision issue
    #mm3d Nuage2Ply MEC-Malt/NuageImProf_STD-MALT_Etape_8.xml  Out=OUTPUT/PointCloud_OffsetUTM.ply Offs=[${X_OFF},${Y_OFF},0]
 
    cd MEC-Malt
    finalDEMs=($(ls Z_Num*_DeZoom*_STD-MALT.tif))
    finalcors=($(ls Correl_STD-MALT_Num*.tif))
    DEMind=$((${#finalDEMs[@]}-1))
    corind=$((${#finalcors[@]}-1))
    lastDEM=${finalDEMs[DEMind]}
    lastcor=${finalcors[corind]}
    laststr="${lastDEM%.*}"
    corrstr="${lastcor%.*}"
    cp $laststr.tfw $corrstr.tfw
    cd ..

    mm3d ConvertIm Ortho-MEC-Malt/Orthophotomosaic.tif 
    cp Ortho-MEC-Malt/Orthophotomosaic.tfw Ortho-MEC-Malt/Orthophotomosaic_Out.tfw
    
    gdal_translate -a_srs "+proj=utm +zone=${UTM} +ellps=WGS84 +datum=WGS84 +units=m +no_defs" Ortho-MEC-Malt/Orthophotomosaic_Out.tif OUTPUT/OrthoImage_geotif.tif
    gdal_translate -a_srs "+proj=utm +zone=${UTM} +ellps=WGS84 +datum=WGS84 +units=m +no_defs" MEC-Malt/$lastDEM OUTPUT/DEM_geotif.tif
    gdal_translate -a_srs "+proj=utm +zone=${UTM} +ellps=WGS84 +datum=WGS84 +units=m +no_defs" MEC-Malt/$lastcor OUTPUT/CORR.tif
fi
