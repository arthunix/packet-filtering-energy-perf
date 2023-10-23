#!/bin/bash

help()
{
   echo "test_2_config_tool: filter at userspace without tracking"
   echo "Syntax: : filter [-h | -d dest. addr | -p dest. port]"
   echo "options:"
   echo "p     Destination Port."
   echo "d     Destination Address."
   echo "h     Print Help."
   echo
}

while getopts ":h:p:d:" option; do
    case $option in
        h)
            help
            exit
            ;;
        d)
            dAddr=$OPTARG
            ;;
        p)
            dPort=$OPTARG
            ;;
        \?)
            echo "error, invalid option"
            exit
            ;;
    esac
done

if [ -z "$dPort" ] || [ -z "$dAddr" ]; then
    echo 'missing -d or -p option' >&2
    echo
    help
    exit 1
fi

sudo iptables -I PREROUTING -t raw    -d $dAddr -p udp --dport $dPort -j NOTRACK
sudo iptables -I INPUT      -t filter -d $dAddr -p udp --dport $dPort -j ACCEPT
