#!/bin/bash


help_usage ()
{
    echo "Example: ./build.sh 3290 1.1 3290"

}


if [ ! -n "$1" ]; 
then
    help_usage
    exit 1
fi


if [ "$#" -eq 3 ];
then 
    echo "******Start build image******"
    /home/build/$1/release/pica8/build.tcl build /home/build/$1/release/pica8/branches/$2 10.10.50.16 $3 1 0 2 1 1 1 1
fi
