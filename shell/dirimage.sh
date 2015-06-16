#!/bin/bash
if [ $# == 0 ] ; then 
    echo "USAGE: $0 TABNAME"
    echo "$0 device Date(ymd) Revision_ID"
    echo " e.g.: $0 3290 20130701 11041"
    echo "-i  device id"
    echo "-v  image file version" 
    echo "-d  image build time" 
    echo "-b  image release mode" 
    echo "-f  image find mode(0=version;1=date;2=version&date" 
    exit 1; 
fi 

while getopts i:v:d:b:f: opt; do
    case $opt in
        i) 
            id=$OPTARG
            ;;
        v)
            version=$OPTARG
            ;; 
        d)
            date=$OPTARG
            ;;
        b)
            builddir=$OPTARG
            ;;
        f)
            finder=$OPTARG
            ;;
    esac
done

if [ -n "$builddir" ]; then
    if [ "$builddir" == "0" ]; then
        dir=/tftpboot/build/daily
    else
        dir=/tftpboot/build/release
    fi
else
    dir=/tftpboot/build/daily
fi
if [ -n "$id" ]; then
    case "$id" in
        3290)
            sDir="$dir/3290/"
            ;;
        3295)
            sDir="$dir/3295/"
            ;;
        3296)
            sDir="$dir/3296/"
            ;;
        3297)
            sDir="$dir/3297/"
            ;;
        3780)
            sDir="$dir/3780/"
            ;;
        3920)
            sDir="$dir/3920/"
            ;;
        3920s)
            sDir="$dir/3920s/"
            ;;
        3922)
            sDir="$dir/3922/"
            ;;
        *)
            echo "The device id does not exist"
            exit 1
            ;;
    esac
else 
    echo "The device id must be exist"
    exit 1
fi


#echo $sDir
if [ -n "$date" ]; then
    date=$(date -d "$date" +%s)
    sFirstDate=$(($date - 86400))
    sLastDate=$(($date + 86400))
else 
    date=$(date +%s)
    sFirstDate=$(($date - 86400))
    sLastDate=$(($date + 86400))
fi
sFirstDate=$(date --date='@'$sFirstDate''  +%Y%m%d)
sLastDate=$(date --date='@'$sLastDate''  +%Y%m%d)
if [ ! -n "$finder" ]; then
     finder=1
fi
#echo "----firstdate--------$sFirstDate"
#echo "----lastdate--------$sLastDate"
#echo "----version--------$version"
#echo "----dir------------$sDir"
#echo "----finder---------$finder"
if [ "$finder" == 2 ]; then
    
    find $sDir -name 'picos-[0-9].[0-9].*' -newermt $sFirstDate ! -newermt $sLastDate |grep $version |awk 'BEGIN{while(getline s) print s;}'
elif [ "$finder" == 1 ]; then
    find $sDir -name 'picos-[0-9.].*' -newermt $sFirstDate ! -newermt $sLastDate |awk 'BEGIN{while(getline s) print s;}'
else 
    if [ -n "$version" ]; then
        find $sDir -name 'picos-[0-9].[0-9].*' |grep $version |awk 'BEGIN{while(getline s) print s;}'
    else
        find $sDir -name 'picos-[0-9].[0-9].*' |awk 'BEGIN{while(getline s) print s;}'
    fi
fi

#echo "----version-----------$sVer"


