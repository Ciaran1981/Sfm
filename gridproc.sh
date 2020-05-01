#

#Created on Mon Oct  1 14:40:35 2018
# Author Ciaran Robb
# Aberystwyth University


# This is a workflow intended for processing very large UAV datasets (eg > 500 images) with MicMac
# Upon testing various configurations with the current version of MicMac,
# some limitations are evident in the use of GPU aided processing which speeds
# up processing considerably.

# This requires an install of MicMac with  potional GPU support if you wish to use that
  

# A parallel processing tool for large scale Malt processing, uses single threads per tile with optional GPU support


# example:
# ./gridproc.sh -e JPG -u "30 +north" -x 6,6 -w 2 -g 1 -b 6


 
# add default values 


 
while getopts ":e:u:s:r:z:e:x:g:b:w:p:t:h" opt; do  
  case ${opt} in
    h)
      echo "Run the grid - workflow for drone acquisition at nadir (and pseudo nadir) angles)."
      echo "gridproc.sh -e JPG -u '30 +north' -x 6 -w 2 -p 4 -b 4"
      echo " -e EXTENSION     : image file type (JPG, jpg, TIF, png..., default=JPG)."
      echo " -u UTMZONE       : UTM Zone of area of interest. Takes form 'NN +north(south)'"
      echo " -s size          : resize of imagery eg - 2000"
      echo " -r RESOL         : Ground resolution (in meters)"
      echo " -z ZoomF         : Last step in pyramidal dense correlation (default=2, can be in [8,4,2,1])"
      echo " -x grd           : Grid dimensions x and y - eg 3,3"
      echo " -g gp            : GPU support 1 for use"
      echo " -b batch         : no of jobs at any one time"
      echo " -w win           : Correl window size"
      echo " -t CSV           : a txt or csv file of gnsss etc - default none - something if needed"
      echo "	-h	          : displays this message and exits."
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
	r) 
      RESOL=${OPTARG}
      ;;  
	z)
      ZoomF=${OPTARG}
      ;;
	x)
      grd=${OPTARG}
      ;;
    g)
      gp=${OPTARG}
      ;;
	w)
      win=${OPTARG}
      ;;
	p)
      proc=${OPTARG}  
      ;;
     t)
      CSV=${OPTARG}
      ;; 
     b)
      batch=${OPTARG} 
      ;;              
    \?)
      echo "gpymicmac.sh: Invalid option: -${OPTARG}" >&1
      exit 1
      ;;
    :)
      echo "gpymicmac.sh: Option -${OPTARG} requires an argument." >&1
      exit 1
      ;;
  esac
done

#mm3d SetExif ."*JPG" F35=45 F=30 Cam=ILCE-6000  
# mogrify -resize 2000 *.JPG


echo "${proc} CPU threads to be used during dense matching, be warned that this has limitations with respect to amount of images processed at a time"
echo "Using GPU support" 


#mm3d SetExif ."*JPG" F35=45 F=30 Cam=ILCE-6000  
# magick convert .*$EXTENSION -resize 50% .*$EXTENSION 

if [  -n "${CSV}" ]; then 
    Orientation.sh -e JPG -u ${UTMZONE} -c Fraser -s ${size} -t ${CSV}
else
    Orientation.sh -e JPG -u ${UTMZONE} -c Fraser -s ${size}
fi
 
 
# Parallel processing - best for a decent ortho later 
if [ -n "${gp}" ]; then
    MaltBatch.py -folder $PWD -algo UrbanMNE -num ${grd} -zr 0.02 -g 1 -nt ${batch} -zoom ${ZoomF} 
else
    MaltBatch.py -folder $PWD -algo UrbanMNE -num ${grd} -zr 0.02 -nt ${batch} -zoom ${ZoomF}
fi

 
orthomosaic.sh -f $PWD -u ${UTM} -mb 1 -mt ossimFeatherMosaic

dsmmosaic.sh -f $PWD -u ${UTM} -mt ossimMaxMosaic


