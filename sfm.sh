# This is a generic workflow for drone imagery which will produce the standard outputs of DSM, Ortho & Point Cloud

# Author Ciaran Robb
# Aberystwyth University

#https://github.com/Ciaran1981/Sfm

while getopts ":e:a:m:u:q:d:i:c:h:" x; do
  case $x in
    h) 
      echo "Complete SfM process outputting DSM, Ortho-Mosaic and Point Cloud."
      echo "Usage: sfm.sh -e JPG -a Forest -m PIMs -u '30 +north' -q 1 -d 1 -i 2000 -c 'mycsv.csv'"
      echo "-e EXTENSION     : image file type (JPG, jpg, TIF, png..., default=JPG)."
      echo "-a Algorithm     : type of algorithm eg Ortho, UrbanMNE for Malt or MicMac, BigMac, QuickMac, Forest, Statue "
      echo "-m MODE          : Either Malt or PIMs - mandatory"
      echo "-u UTMZONE       : UTM Zone of area of interest. Takes form 'NN +north(south)'"
      echo "-q egal          : radiometric eq (See mm3d Tawny)"
      echo "-d DEQ           : Degree of radiometric eq between images during mosaicing (See mm3d Tawny)" 
      echo "-i SIZE          : image resize for processing (OPTIONAL, but recommend half long axis of image) "  
      echo "-c CSV           : Optional (no need if using exif GPS) - text file usually csv with mm3d formatting with image names and gps coords "          
      echo "-h	             : displays this message and exits."
      echo " "
      exit 0 
      ;;    
	e)   
      EXTENSION=$OPTARG 
      ;;
        a)
      Algorithm=$OPTARG
      ;;
        m)
      MODE=$OPTARG
      ;;
	u)
      UTM=$OPTARG
      ;;
	q)
      egal=$OPTARG
      ;;
	d)
      DEQ=$OPTARG  
      ;;
 	i)
      SIZE=${OPTARG}
      ;;            
        c)
      CSV=${OPTARG}
      ;;       
    \?)
      echo "sfm.sh: Invalid option: -$OPTARG" >&1
      exit 1
      ;;
    :)
      echo "sfm.sh: Option -$OPTARG requires an argument." >&1
      exit 1
      ;;
  esac
done

shift $((OPTIND-1))

echo "params chosen are: -e ${EXTENSION} -a ${Algorithm} -m ${MODE} -u ${UTM} -q ${egal} -d ${DEQ} -i ${SIZE} -c ${CSV}"
 

# Use the orientation script....
if [  -f "${CSV}" ]; then 
    Orientation.sh -e ${EXTENSION}  -u ${UTM} -c Fraser  -t "${CSV}" -i ${SIZE}
else
    Orientation.sh -e ${EXTENSION} -u ${UTM} -c Fraser -i ${SIZE}
fi

# Dense cloud etc - default to produce  everything otherwise arg list will be far too long - some params assumed...
# if you want more control use substages or direct mm3d cmds
if [[ "$MODE" = "PIMs" ]]; then 
     dense_cloud.sh -e ${EXTENSION} -a ${Algorithm} -m PIMs -i ${egal} -d ${DEQ} -o 1
else
     dense_cloud.sh -e ${EXTENSION} -a ${Algorithm} -m Malt -i ${egal} -d ${DEQ} -o 1
fi


