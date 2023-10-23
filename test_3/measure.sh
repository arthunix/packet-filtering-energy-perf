#!/bin/bash

help()
{
   echo "test_3_measure: filter at socket (bpf: berkeley packet filter)"
   echo "Syntax: : filter [-h | -f filename]"
   echo "options:"
   echo "f     Name of The File."
   echo "h     Print Help."
   echo
}

while getopts ":h:f:" option; do
    case $option in
        h)
            help
            exit
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

if [ -z "$fName" ]; then
    echo 'missing -f option' >&2
    echo
    help
    exit 1
fi

while true
do
    sudo mpstat -u -I SUM -P ALL 1 1 | grep -E -v Aver >> $fName
done