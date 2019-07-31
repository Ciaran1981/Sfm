# This is for oblique imagery - a work in progress
# The main difference here is using the C3DC algorithm at the end of the process to produce a point cloud
# It has been written with testing things out in mind, with hefty datasets covered by the other scripts

#@author: Ciaran Robb

#https://github.com/Ciaran1981/Sfm
# Based on a L.Girod script - credit to him!
# Aberystwyth University


# add default values


while getopts "e:a:m:d:z:h" opt; do
  case $opt in
    h)
      echo "Run workflow for point cloud from culture 3d algo."
      echo "usage: Oblique.sh -e JPG -a Statue -d 10 -z 2"
      echo "	-e EXTENSION   : image file type (JPG, jpg, TIF, png..., default=JPG)."
      echo "	-a Algorithm   : type of algo eg BigMac, MicMac, Forest, Statue etc."
      echo "	-m match       : matching type - eg Line All etc" 
      echo "	-csv CSV       : Whether to use a csv file."
      echo "	-u UTM         : UTM zone."
      echo "	-z ZOOM        : Zoom Level (default=2)"
      echo "	-h	  : displays this message and exits."
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
      match=$OPTARG 
      ;;        
	z)
      ZOOM=$OPTARG
      ;;
	s)
      use_Schnaps=true
      ;; 
	d)
      dist=$OPTARG
      ;; 
    \?)
      echo "Oblique.sh: Invalid option: -$OPTARG" >&1
      exit 1
      ;;
    :)
      echo "Oblique.sh: Option -$OPTARG requires an argument." >&1
      exit 1
      ;; 
  esac
done



# If the camera positions are all over the shop its better to use the ALL option
if [  -n "$match" ]; then
    echo "Matching type specified"
    mm3d Tapioca $match .*$EXTENSION -1 @SFS
else
    mm3d Tapioca File FileImagesNeighbour.xml -1 @SFS
fi


mm3d Schnaps .*$EXTENSION MoveBadImgs=1 

#Compute Relative orientation (Arbitrary system)
mm3d Tapas Fraser .*$EXTENSION Out=Arbitrary SH=_mini

# This lot screws it up when not all nadir!!!! 
#Transform to  RTL system
#mm3d CenterBascule .*$EXTENSION Arbitrary RAWGNSS_N Ground_Init_RTL

#Change system to final cartographic system  


mm3d AperiCloud .*$EXTENSION Arbitrary WithCam=0 SH=_mini Out=Arbitrary.ply
mm3d AperiCloud .*$EXTENSION Arbitrary SH=_mini Out=withcams.ply



  
#HERE, MASKING COULD BE DONE!!!

mm3d SaisieMasqQT Arbitrary.ply
read -rsp $'Press any key to continue...\n' -n1 key
mm3d C3DC $Algorithm .*$EXTENSION Arbitrary ZoomF=$ZOOM Masq3D=Arbitrary_polyg3d.xml  Out=Dense.ply
mm3d TiPunch Dense.ply Mode=$Algorithm Pattern=.*$EXTENSION

mm3d Tequila .*$EXTENSION Arbitrary Dense_poisson_depth8.ply Filter=1



