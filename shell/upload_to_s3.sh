#!/bin/bash
DAYS=$1
date1=$(date +"%s")
echo "Syncing images for ${DAYS} last days"
# LIST=`find /tftpboot/build/daily/ ! -name *picos-1.1* ! -name *pica_bin-1.1* -name *.tar.gz -mtime -${DAYS}`
LIST=`find /tftpboot/build/daily/ ! -name onie-installer-*.tar.gz -name *.bin -name *.tar.gz -mtime -${DAYS}`
echo ""
NUMBER_END=`find /tftpboot/build/daily/ -name *.tar.gz -mtime -${DAYS} | wc -l`
echo "Found images was last modified last ${DAYS} day(s): ${NUMBER_END}"
echo ""
NUMBER=1
SUCCESS=0
UPLOADEDBYTES=0
SKIP=0
for item in $LIST
do
  echo ""
  echo "Sync ${NUMBER} of ${NUMBER_END} image"
  FOLDER=$(echo $item | sed -e 's/\/tftpboot\/build\/daily\///' | sed -e 's/\/.*\.tar\.gz$//')
  FILE=$(echo $item | sed 's/.*\(\/.*\.tar\.gz$\)/\1/')
  SIZE=`s3cmd ls s3://pica8-images/daily/$FOLDER$FILE | awk '{print($3)}'`
  SIZELOC=`ls -la $item | awk '{print($3)}'`
  if [[ $SIZE -ne "" ]] 
  then
    MD5S3=`s3cmd info s3://pica8-images/daily/$FOLDER$FILE | grep "MD5 sum:" | sed "s/   MD5 sum:   //"`
    MD5LOC=`md5sum $item | awk '{print($1)}'`
    if [ $MD5S3 == $MD5LOC ]
    then
      echo "The image $item has already uploaded to s3"
      SKIP=+1
    else
      echo "Local and S3 are not same"
      echo "Uploading ..."
      /usr/bin/s3cmd sync --no-progress -dv $item s3://pica8-images/daily/$FOLDER$FILE
      SUCCESS=+1
      UPLOADEDBYTES=+$SIZELOC
    fi
  else
    echo "Uploading ..."
    /usr/bin/s3cmd sync --no-progress -dv $item s3://pica8-images/daily/$FOLDER$FILE
  fi
  NUMBER=$((NUMBER+1))
done
date2=$(date +"%s")
diff=$(($date2-$date1))
echo $SUCCESS $SKIP $UPLOADEDBYTES $diff
