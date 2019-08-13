# Author Ciaran Robb
# Aberystwyth University
# Using GDAL and OSSIM, create a large scale ortho-mosaic from a set of smaller ones generated by the batch fucntions here:
# https://github.com/Ciaran1981/Sfm


# add default values



 
while getopts "f:u:mb:pb:mt:o:h" opt; do  
  case $opt in
    h)
      echo "Run an ossim-based ortho-mosaic on micmac derived imagery"
      echo "orthomosaic.sh -f $PWD -u '30 +north' -mt ossimFeatherMosaic -o outmosaic.tif"
      echo "	-f FOLDER     : MicMac working directory or Malt/PIMs ortho dir."
      echo "	-u UTMZONE    : UTM Zone of area of interest"
      echo "    -mb MBATCH    : whether to us maltbatch (bool) "
      echo "    -pb PBATCH    : whether to us pimsbatch (bool)"      
      echo "    -mt MTYPE     : OSSIM mosaicing type e.g. ossimBlendMosaic ossimMaxMosaic ossimImageMosaic ossimClosestToCenterCombiner ossimBandMergeSource ossimFeatherMosaic" 
      echo "	-o OUT        : Output mosaic e.g. mosaic.tif"      
      echo "	-h	          : displays this message and exits."
      
      echo " " 
      exit 0
      ;;    
	f)
      FOLDER=$OPTARG 
      ;;
	u)
      UTM=$OPTARG
      utm_set=true
      ;;
	mb)
      MBATCH=$OPTARG
      ;;   
	pb)
      PBATCH=$OPTARG
      ;;   
	mt)
      MTYPE=$OPTARG
      ;;                        
	o)
      OUT=$OPTARG
      ;;        
    \?)
      echo "orthomosaic.sh: Invalid option: -$OPTARG" >&1
      exit 1
      ;;
    :)
      echo "orthomosaic.sh: Option -$OPTARG requires an argument." >&1
      exit 1
      ;;
  esac
done

if [ -n "${MBATCH}" ]; then

    echo "geo-reffing  mini ortho-mosaics generated from Malt/Pims/TawnyBatch"

    #if [ -n "${tile}" ]; then
    for f in $FOLDER/MaltBatch/*tile*/*Ortho-tile*/*Orthophotomosaic.tif; do
        gdal_edit.py -a_srs "+proj=utm +zone=$UTM  +ellps=WGS84 +datum=WGS84 +units=m +no_defs" "$f"; done
    
       
    # this works 
    echo "generating image histograms"
    find $FOLDER/MaltBatch/*tile*/*Ortho-tile*/*Orthophotomosaic.tif | parallel "ossim-create-histo -i {}" 
     
    # Max seems best
    echo "creating final mosaic"
    ossim-orthoigen --combiner-type $MTYPE  $FOLDER/MaltBatch/*tile*/*Ortho-tile*/*Orthophotomosaic.tif $OUT
fi

if [ -n "${PBATCH}" ]; then

    echo "geo-reffing  mini ortho-mosaics generated from Malt/Pims/TawnyBatch"

    #if [ -n "${tile}" ]; then
    for f in $FOLDER/MaltBatch/*tile*/*Ortho-tile*/*Orthophotomosaic.tif; do
        gdal_edit.py -a_srs "+proj=utm +zone=$UTM  +ellps=WGS84 +datum=WGS84 +units=m +no_defs" "$f"; done
    
       
    # this works 
    echo "generating image histograms"
    find $FOLDER/MaltBatch/*tile*/*Ortho-tile*/*Orthophotomosaic.tif | parallel "ossim-create-histo -i {}" 
     
    # Max seems best
    echo "creating final mosaic"
    ossim-orthoigen --combiner-type $MTYPE  $FOLDER/MaltBatch/*tile*/*Ortho-tile*/*Orthophotomosaic.tif $OUT
else
    #for f in $FOLDER/*Ort_*tif; do
       # mm3d ConvertIm "$f"; done
        
    for f in $FOLDER/*Ort_*tif; do
        gdal_edit.py -a_srs "+proj=utm +zone=$UTM  +ellps=WGS84 +datum=WGS84 +units=m +no_defs" "$f"; done
    
       
    # this works 
    echo "generating image histograms"
    find $FOLDER/*Ort_*tif | parallel "ossim-create-histo -i {}" 
     
    # Max seems best
    echo "creating final mosaic"
    ossim-orthoigen --combiner-type $MTYPE  $FOLDER/*Ort_*tif $OUT
fi    