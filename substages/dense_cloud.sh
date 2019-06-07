
#Created on Fri May  3 17:23:41 2019

#https://github.com/Ciaran1981/Sfm

#A shell script to process the dense cloud only using the PIMs algorithm

#Purely for convenience

#Usage dense_cloud.sh -e JPG -a Forest -u 30 +north -z 4 -r 0.02



while getopts ":e:a:u:z:d:g:p:r:o:s:h" opt; do
  case $opt in
    h)  
      echo "Process dense cloud."
      echo "Usage: dense_cloud.sh -e JPG -a Forest -z 4 -r 0.02"
      echo "	-e EXTENSION     : image file type (JPG, jpg, TIF, png..., default=JPG)."
      echo "	-a Algorithm     : type of algo eg BigMac, MicMac, Forest, Statue etc"
      echo "	-u UTMZONE       : UTM Zone of area of interest. Takes form 'NN +north(south)'"
      echo "	-z ZoomF         : Last step in pyramidal dense correlation (default=2, can be in [8,4,2,1])"
      echo "	-d DEQ          : Degree of equalisation between images during mosaicing (See mm3d Tawny)"
      echo " -g gpu           : Whether to use GPU support, default false"
      echo " -p            : no chunks to split the data into for gpu processing"
      echo " -r              : zreg term - context dependent "     
      echo " -o              : do ortho - 0 or 1 "           
      echo " -s              : do ortho - 0 or 1 "    
      echo "	-h	             : displays this message and exits."
      echo " "
      exit 0 
      ;;    
	e)   
      EXTENSION=${OPTARG} 
      ;;
    a)
      Algorithm=${OPTARG}
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
	g)
      gpu=${OPTARG}
      ;; 
    p)
      prc=${OPTARG}
      ;; 
    r)
      zreg=${OPTARG}
      ;;
    o)
      orth=${OPTARG}
      ;;
    s)
      samp=${OPTARG}
      ;;
    \?)
      echo "DronePIMs.sh: Invalid option: -${OPTARG}" >&1
      exit 1
      ;;
    :)
      echo "DronePIMs.sh: Option -${OPTARG} requires an argument." >&1
      exit 1
      ;;
  esac
done

mkdir OUTPUT


mm3d PIMs $Algorithm .*${EXTENSION} Ground_UTM DefCor=0 ZoomF=$ZoomF ZReg=$zreg SH=_mini  

if [ -n "${orth}" ]
    mm3d PIMs2MNT $Algorithm DoMnt=1 DoOrtho=1
	 
    if [ -n "${DEQ}" ]; then
        mm3d Tawny PIMs-ORTHO/ RadiomEgal=${DEQ} Out=Orthophotomosaic.tif
    else
        mm3d Tawny PIMs-ORTHO/ RadiomEgal=0 Out=Orthophotomosaic.tif
   

    mm3d ConvertIm PIMs-ORTHO/Orthophotomosaic.tif Out=OUTPUT/OrthFinal.tif
    cp PIMs-ORTHO/Orthophotomosaic.tfw OUTPUT/OrthFinal.tfw
    gdal_edit.py -a_srs "+proj=utm +zone=$UTM +ellps=WGS84 +datum=WGS84 +units=m +no_defs" OUTPUT/OrthFinal.tif
    mm3d Nuage2Ply PIMs-TmpBasc/PIMs-Merged.xml Attr=PIMs-ORTHO/Orthophotomosaic.tif Out=OUTPUT/pointcloud.ply
else
    mm3d PIMs2MNT $Algorithm DoMnt=1 
fi

mask_dsm.py -folder $PWD -pims 1


cp PIMs-TmpBasc/PIMs-Merged_Prof.tfw OUTPUT/DSM.tfw
cp PIMs-TmpBasc/PIMs-Merged_Prof.tif OUTPUT/DSM.tif
cp PIMs-TmpBasc/PIMs-Merged_Masq.tif OUTPUT/Mask.tif
cp PIMs-TmpBasc/PIMs-Merged_Prof.tfw OUTPUT/Mask.tfw
cp PIMs-TmpBasc/PIMs-Merged_Prof.tfw OUTPUT/Corr.tfw
cp PIMs-TmpBasc/PIMs-Merged_Correl.tif OUTPUT/Corr.tif

gdal_edit.py -a_srs "+proj=utm +zone=${UTM}  +ellps=WGS84 +datum=WGS84 +units=m +no_defs" DSM.tif
gdal_edit.py -a_srs "+proj=utm +zone=${UTM}  +ellps=WGS84 +datum=WGS84 +units=m +no_defs" Mask.tif
gdal_edit.py -a_srs "+proj=utm +zone=${UTM}  +ellps=WGS84 +datum=WGS84 +units=m +no_defs" Corr.tif   
 


