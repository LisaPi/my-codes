#!/bin/bash


help_usage ()
{
    echo "Usage: ./build.sh model branch  model type license dversion"
    echo "Example: ./build.sh 3290 1.1 3290  1 1"
    echo "model : the platform model"
    echo "branch : the code branches"
    echo "type : svn type"
}


if [ ! -n "$1" ]; 
then
    help_usage
    exit 1
fi


if [ "$#" -eq 4 ];
then
  echo "******Start build image******"
  /home/build/$1/release/pica8/build-new.tcl build /home/build/$1/release/pica8/branches/$2 10.10.50.16 $3  $4  0 1
fi
