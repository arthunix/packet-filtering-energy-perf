#!/bin/bash

help()
{
   echo "test_7_config_tool: filter at kernel netfilter (nftables ingress)"
   echo "Syntax: : filter [-h | -i interface | -d dest. addr | -p dest. port]"
   echo "options:"
   echo "i     Network Interaface."
   echo "p     Destination Port."
   echo "d     Destination Address."
   echo "h     Print Help."
   echo
}

while getopts ":h:i:p:d:" option; do
    case $option in
        h)
            help
            exit
            ;;
        i)
            iFace=$OPTARG
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

if [ -z "$dPort" ] || [ -z "$dAddr" ] || [ -z "$iFace" ]; then
    echo 'missing -d or -p or -i option' >&2
    echo
    help
    exit 1
fi

sudo tc qdisc add dev $iFace ingress
sudo tc filter add dev $iFace parent ffff: prio 4 protocol ip u32 match ip protocol 17 0xff match ip dport $dPort 0xffff match ip dst $dAddr flowid 1:1 action drop