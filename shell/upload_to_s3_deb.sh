#!/bin/bash
ROOT=$1
RELEASE=$2
cd $ROOT
LIST=`find ./ -name '*.deb' `
echo ""
for item in $LIST
do
  echo ""
  item=$(echo $item | sed -e 's/\.\///' )
  echo "Sync ${item}"
  /usr/bin/s3cmd sync --no-progress -dv $item s3://pica8-releases/$RELEASE/$item
done
