# This is a generic workflow for drone imagery which will produce the standard outputs of DSM, Ortho & Point Cloud

# Author Ciaran Robb
# Aberystwyth University

#https://github.com/Ciaran1981/Sfm

while getopts ":e:a:c:m:u:i:t:h:" x; do
  case $x in
    h) 
      echo "Complete SfM process outputting DSM, Ortho-Mosaic and Point Cloud."
      echo "Usage: mspec_sfm.sh -e tif -a Ortho -m Malt -u '30 +north' -c Fraser -t mycsv.csv"
      echo "-e EXTENSION     : image file type (JPG, jpg, TIF, png..., default=JPG)."
      echo "-a Algorithm     : type of algorithm eg Ortho, UrbanMNE for Malt or MicMac, BigMac, QuickMac, Forest, Statue "
      echo "-c CALIB         : Camera calibration model - e.g. RadialBasic, Fraser etc"
      echo "-m MODE          : Either Malt or PIMs - mandatory"
      echo "-u UTMZONE       : UTM Zone of area of interest. Takes form 'NN +north(south)'"
      echo "-i SIZE          : image resize for processing (OPTIONAL, but recommend half long axis of image) "  
      echo "-t CSV           : Optional (no need if using exif GPS) - text file usually csv with mm3d formatting with image names and gps coords"          
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
        c)
      CALIB=$OPTARG
      ;;
        m)
      MODE=$OPTARG
      ;;  
	u)
      UTM=$OPTARG
      ;;
 	i)
      SIZE=${OPTARG}
      ;;            
        t)
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

echo "params chosen are: -e ${EXTENSION} -a ${Algorithm} -c ${CALIB} -m ${MODE} -u ${UTM} -i ${SIZE} -c ${CALIB}" -t ${CSV}
 


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

mv RGB/*.tif $PWD

if [  -f "${CSV}" ]; then 
    echo "using csv file ${CSV}"  
    mm3d OriConvert OriTxtInFile ${CSV} RAWGNSS_N ChSys=DegreeWGS84@SysUTM.xml MTD1=1  NameCple=FileImagesNeighbour.xml CalcV=1
    sysCort_make.py -csv ${CSV} -d " "  
else 
    echo "using exif data"
    mm3d XifGps2Txt .*${EXTENSION}
    # here as the transform always screws up with xml
    sed -i '1s/^/#F=N X Y Z\n/' GpsCoordinatesFromExif.txt 
    mm3d OriConvert OriTxtInFile GpsCoordinatesFromExif.txt RAWGNSS_N ChSys=DegreeWGS84@SysUTM.xml MTD1=1  NameCple=FileImagesNeighbour.xml CalcV=1
    sysCort_make.py -csv GpsCoordinatesFromExif.txt -d " "
fi 


if [  -n "${SIZE}" ]; then
    echo "resizing to ${SIZE} for tie point detection"
    # mogrify -path Sharp -sharpen 0x3  *.JPG # this sharpens very well worth doing
    mogrify -resize ${SIZE} *.${EXTENSION}
fi

mm3d Tapioca File FileImagesNeighbour.xml -1  @SFS


mm3d Schnaps .*${EXTENSION} MoveBadImgs=1
# The sh doesn't seem to work in PIMs etc so best to rename and thus we have reduced set
mv Homol HomolInit1
mv Homol_mini Homol

#Compute Relative orientation (Arbitrary system)


mm3d Martini .*${EXTENSION}

mm3d Tapas ${CALIB} .*${EXTENSION} Out=Arbitrary InCal=Martini | tee ${CALIB}RelBundle.txt
  
#Visualize relative orientation

mm3d AperiCloud .*${EXTENSION} Ori-Arbitrary 


mm3d CenterBascule .*${EXTENSION} Arbitrary RAWGNSS_N Ground_Init_RTL


#Visualize Ground_RTL orientation
mm3d AperiCloud .*${EXTENSION} Ori-Ground_Init_RTL 

#Bundle adjust using both camera positions and tie points (number in EmGPS option is the quality estimate of the GNSS data in meters)
#Change system to final cartographic system  

mm3d Campari .*${EXTENSION} Ground_Init_RTL Ground_UTM EmGPS=[RAWGNSS_N,1] AllFree=1  | tee ${CALIB}GnssBundle.txt


mm3d AperiCloud .*${EXTENSION} Ground_UTM


dense_cloud.sh -e ${EXTENSION} -a ${Algorithm} -m ${MODE} -u ${UTM} -x 1  

mv *.tif RGB

mv OUTPUT/OrthoImage_geotif.tif OUTPUT/RGB.tif
mv OUTPUT/PointCloud_OffsetUTM.ply OUTPUT/RGB.ply
rm -rf OUTPUT/OrthoImage_geotif.tif
rm -rf OUTPUT/PointCloud_OffsetUTM.ply

mv RRENir/*.tif $PWD

dense_cloud.sh -e ${EXTENSION} -a ${Algorithm} -m ${MODE} -u ${UTM} -x 0

mv *.tif RRENir

mv OUTPUT/OrthoImage_geotif.tif OUTPUT/RRENir.tif
mv OUTPUT/PointCloud_OffsetUTM.ply OUTPUT/RRENir.ply
rm -rf OUTPUT/OrthoImage_geotif.tif
rm -rf OUTPUT/PointCloud_OffsetUTM.ply

echo "results in the output folder" 

##################################################################################################################################################
# Way less verbose but certain params are not parsed by orientation subscript - given up trying for moment - perhaps someone can figure it out!! #!##################################################################################################################################################
# Use the orientation script....
#if [  -f "${CSV}" ]; then 
#    Orientation.sh -e ${EXTENSION}  -u ${UTM} -c ${CALIB}  -t ${CSV} -i ${SIZE}
#else
#    Orientation.sh -e ${EXTENSION} -u ${UTM} -c ${CALIB} -i ${SIZE}
#fi

# Dense cloud etc - default to produce  everything otherwise arg list will be far too long - some params assumed...
# if you want more control use substages or direct mm3d cmds
#if [[ "$MODE" = "PIMs" ]]; then 
#     dense_cloud.sh -e ${EXTENSION} -a ${Algorithm} -m ${MODE} -i ${egal} -d ${DEQ} -o 1
#else
#     dense_cloud.sh -e ${EXTENSION} -a ${Algorithm} -m ${MODE} -i ${egal} -d ${DEQ} -o 1
#fi


