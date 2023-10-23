#!/bin/bash

help()
{
   echo "test_8_measure: filter at kernel scheduling (traffic control - tc)"
   echo "Syntax: : filter [-h | -f filename | -i interface]"
   echo "options:"
   echo "f     Name of The File."
   echo "i     Network Interface"
   echo "h     Print Help."
   echo
}

while getopts ":h:f:i:" option; do
    case $option in
        h)
            help
            exit
            ;;
        i)
            iFace=$OPTARG
            ;;
        f)
            fName=$OPTARG
            ;;
        \?)
            echo "error, invalid option"
            exit
            ;;
    esac
done

if [ -z "$fName" ] || [ -z "$iFace" ]; then
    echo 'missing -f option' >&2
    echo
    help
    exit 1
fi

while true
do
    sudo tc -s filter show dev $iFace ingress >> $fName && mpstat -u -I SUM -P ALL 1 1 | grep -E -v Aver >> $fName
done
