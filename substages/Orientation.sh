# This script detects tie/key points, orients imagery in relative space then
# adjusts using GNSS data 

# Author Ciaran Robb
# Aberystwyth University

#https://github.com/Ciaran1981/Sfm
# example:
# Orientation.sh -e JPG -u "30 +north" -i 3000 -c Fraser -t Log_edited.csv -s sub.csv




while getopts ":e:u:i:c:t:s:sz:h:" o; do  
  case ${o} in
    h)
      echo "Carry out feature extraction and orientation of images"
      echo "Usage: Orientation.sh -e JPG -u 30 +north -sub sub.csv " 
      echo "	-e {EXTENSION}     : image file type (JPG, jpg, TIF, png..., default=JPG)."
      echo "	-u UTMZONE       : UTM Zone of area of interest. Takes form 'NN +north(south)'"
      echo "	-s SIZE         : resize of imagery eg - 2000"
      echo "	-c CALIB        : Camera calibration model - e.g. RadialBasic, Fraser etc"
      echo "-t -CSV        : text file usually csv with mm3d formatting"
      echo "-s -SUB        : a subset  csv for pre-calibration of orientation"      
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
 	i)
      SIZE=${OPTARG}
      ;; 
 	c)
      CALIB=${OPTARG}
      ;;        
    t)
      CSV=${OPTARG}
      ;; 
    s)
      SUB=${OPTARG}
      ;;
    sz)
      SUB=${SIZE}
      ;;                    
    \?)
      echo "Orientation.sh: Invalid option: -${OPTARG}" >&1
      exit 1
      ;;
    :)
      echo "Orientation.sh: Option -${OPTARG} requires an argument." >&1
      exit 1
      ;;
  esac
done

shift $((OPTIND-1))


#mm3d SetExif ."*{EXTENSION}" F35=45 F=30 Cam=ILCE-6000  
# magick mogrify -resize 50%

#create UTM file (after deleting any existing one)
rm SysUTM.xml
echo "<SystemeCoord>                                                                                              " >> SysUTM.xml
echo "         <BSC>                                                                                              " >> SysUTM.xml
echo "            <TypeCoord>  eTC_Proj4 </TypeCoord>                                                             " >> SysUTM.xml
echo "            <AuxR>       1        </AuxR>                                                                   " >> SysUTM.xml
echo "            <AuxR>       1        </AuxR>                                                                   " >> SysUTM.xml
echo "            <AuxR>       1        </AuxR>                                                                   " >> SysUTM.xml
echo "            <AuxStr>  +proj=utm +zone="$UTM "+ellps=WGS84 +datum=WGS84 +units=m +no_defs   </AuxStr>        " >> SysUTM.xml
echo "                                                                                                            " >> SysUTM.xml
echo "         </BSC>                                                                                             " >> SysUTM.xml
echo "</SystemeCoord>                                                                                             " >> SysUTM.xml
  

#mm3d SetExif ."*JPG" F35=45 F=30 Cam=ILCE-6000  
# mogrify -resize 30% *.JPG
#mogrify -resize 2000 *.JPG

if [  -n "${CSV}" ]; then 
    echo "using csv file ${CSV}"  
    mm3d OriConvert OriTxtInFile ${CSV} RAWGNSS_N ChSys=DegreeWGS84@SysUTM.xml MTD1=1  NameCple=FileImagesNeighbour.xml CalcV=1
    sysCort_make.py -csv ${CSV} -d " "  
else 
    echo "using exif data"
    mm3d XifGps2Txt .*${EXTENSION} 
    #Get the GNSS data out of the images and convert it to a xml orientation folder (Ori-RAWGNSS), also create a good RTL (Local Radial Tangential) system.
    mm3d XifGps2Xml .*${EXTENSION} RAWGNSS
    mm3d OriConvert "#F=N X Y Z" GpsCoordinatesFromExif.txt RAWGNSS_N ChSys=DegreeWGS84@RTLFromExif.xml MTD1=1 NameCple=FileImagesNeighbour.xml CalcV=1
fi 


if [  -n "${SIZE}" ]; then
    echo "resizing to ${SIZE} for tie point detection"
    # mogrify -path Sharp -sharpen 0x3  *.JPG # this sharpens very well worth doing
    mogrify -resize ${SIZE} *.${EXTENSION}
fi

mm3d Tapioca File FileImagesNeighbour.xml -1  @SFS


mm3d Schnaps .*${EXTENSION} MoveBadImgs=1

#Compute Relative orientation (Arbitrary system)

if [  -n "${SUB}" ]; then
    echo "using calibration subset"
    calib_subset.py -folder $PWD -algo ${CALIB}  -csv ${SUB} -ext .${EXTENSION}
else
    mm3d Tapas ${CALIB} .*${EXTENSION} Out=Arbitrary SH=_mini | tee ${CALIB}RelBundle.txt
    echo " orientation using whole dataset"
fi    


#Visualize relative orientation

mm3d AperiCloud .*${EXTENSION} Ori-Arbitrary SH=_mini


#Transform to  RTL system
mm3d CenterBascule .*${EXTENSION} Arbitrary RAWGNSS_N Ground_Init_RTL


#Visualize Ground_RTL orientation
mm3d AperiCloud .*${EXTENSION} Ori-Ground_Init_RTL SH=_mini

#Bundle adjust using both camera positions and tie points (number in EmGPS option is the quality estimate of the GNSS data in meters)
 
#Change system to final cartographic system  
if [  -n "${CSV}" ]; then 
    mm3d Campari .*${EXTENSION} Ground_Init_RTL Ground_UTM EmGPS=[RAWGNSS_N,1] AllFree=1 SH=_mini | tee ${CALIB}GnssBundle.txt
    # For reasons unknown this screws it up from csv
    #mm3d ChgSysCo  .*${EXTENSION} Ground_RTL SysCoRTL.xml@SysUTM.xml Ground_UTM
else
    mm3d Campari .*${EXTENSION} Ground_Init_RTL Ground_RTL EmGPS=[RAWGNSS_N,1] AllFree=1 SH=_mini | tee ${CALIB}GnssBundle.txt
    mm3d ChgSysCo  .*${EXTENSION} Ground_RTL RTLFromExif.xml@SysUTM.xml Ground_UTM
    mm3d OriExport Ori-Ground_UTM/.*xml CameraPositionsUTM.txt AddF=1
fi


mm3d AperiCloud .*${EXTENSION} Ground_UTM SH=_mini