# This is a generic workflow for drone imagery using the malt pipeline

# Author Ciaran Robb
# Aberystwyth University

#https://github.com/Ciaran1981/Sfm
# example:
# ./Drone.sh -e JPG -u "30 +north" -g 1 -w 2 -p 20

 

# add default values 


 
while getopts "e:u:s:z:d:g:p:t:h" opt; do  
  case ${opt} in
    h)
      echo "Run the workflow for drone acquisition at nadir (and pseudo nadir) angles)."
      echo "usage: Drone.sh -e JPG -u "30 +north" -p 16 
      echo "	-e EXTENSION     : image file type (JPG, jpg, TIF, png..., default=JPG)."
      echo "	-u UTMZONE       : UTM Zone of area of interest. Takes form 'NN +north(south)'"
      echo "	-s size         : resize of imagery eg - 2000"
      echo "	-z ZoomF         : Last step in pyramidal dense correlation (default=2, can be in [8,4,2,1])"
      echo "	-d DEQ          : Degree of equalisation between images during mosaicing (See mm3d Tawny)"
      echo " -g gpu           : Whether to use GPU support -g 1 for use exclude otherwise "
      echo " -p proc        : no of CPU thread used (needed even when using GPU)"
      echo " -t -CSV        : a txt file or csvwithh coords in mm3d format "
      echo "	-h	             : displays this message and exits."
      echo " "  
      exit 0
      ;;    
	e)
      EXTENSION=${OPTARG}
      ;;
	u)
      UTM=${OPTARG}
      ;;
 	s)
      size=${OPTARG}
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
      proc=${OPTARG}  
      ;; 
    t)
      CSV=${OPTARG}
      ;;         
    \?)
      echo "Drone.sh: Invalid option: -${OPTARG}" >&1
      exit 1
      ;;
    :)
      echo "Drone.sh: Option -${OPTARG} requires an argument." >&1
      exit 1
      ;;
  esac
done


#mm3d SetExif ."*JPG" F35=45 F=30 Cam=ILCE-6000  
# magick mogrify -resize 50%


if [  -n "${CSV}" ]; then 
    Orientation.sh -e JPG -u ${UTMZONE} -c Fraser -sz ${size} -csv ${CSV}
else
    Orientation.sh -e JPG -u ${UTMZONE} -c Fraser -sz ${size}
fi
#Correlation into DEM 
 
if [ -n "${gpu}" = true ]; then 
    	/home/ciaran/MicMacGPU/micmac/bin/mm3d Malt UrbanMNE ".*.${EXTENSION}" Ground_UTM UseGpu=1 EZA=1 DoOrtho=1 SzW=${win} ZoomF=${ZoomF} NbProc=${proc}
else
	mm3d Malt Ortho ".*.${EXTENSION}" Ground_UTM UseGpu=0 EZA=1 DoOrtho=1 SzW=${win} ZoomF=${ZoomF} NbProc=${proc}
fi

if [ -n "${DEQ}" ]; then 
    mm3d Tawny Ortho-MEC-Malt RadiomEgal=1 
else
    mm3d Tawny Ortho-MEC-Malt RadiomEgal=1 
fi

#Making OUTPUT folder
mkdir OUTPUT
#PointCloud from Ortho+DEM, with offset substracted to the coordinates to solve the 32bit precision issue
mm3d Nuage2Ply MEC-Malt/NuageImProf_STD-MALT_Etape_8.xml Attr=Ortho-MEC-Malt/Orthophotomosaic.tif Out=OUTPUT/PointCloud_OffsetUTM.ply Offs=[${X_OFF},${Y_OFF},0]
 
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

mm3d ConvertIm Ortho-MEC-Malt/Orthophotomosaic.tif Out=OrthFinal.tif

gdal_translate -a_srs "+proj=utm +zone=${UTM} +ellps=WGS84 +datum=WGS84 +units=m +no_defs" Ortho-MEC-Malt/OrthFinal.tif OUTPUT/OrthoImage_geotif.tif
gdal_translate -a_srs "+proj=utm +zone=${UTM} +ellps=WGS84 +datum=WGS84 +units=m +no_defs" MEC-Malt/$lastDEM OUTPUT/DEM_geotif.tif
gdal_translate -a_srs "+proj=utm +zone=${UTM} +ellps=WGS84 +datum=WGS84 +units=m +no_defs" MEC-Malt/$lastcor OUTPUT/CORR.tif
