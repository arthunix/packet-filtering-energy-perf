#!/bin/bash

help()
{
   echo "Syntax: packet_filtering_rules_clean [-h | -d dest. addr | | -p dest. port | -i interface | -s pkt. size]"
   echo "options:"
   echo "i     Interface."
   echo "p     Destination Port."
   echo "d     Destination Address."
   echo "s     Packet Size."
   echo "h     Print Help."
   echo
}

while getopts ":hi:p:d:s:" option; do
    case $option in
        h)
            help
            exit;;
        i)
            destination_ifce=$OPTARG
            ;;
        p)
            destination_port=$OPTARG
            ;;
        d)
            destination_addr=$OPTARG
            ;;
        s)
            generat_pkt_size=$OPTARG
            ;;
        \?)
            echo "error, invalid option"
            exit;;
    esac
done

if [ -z "$destination_port" ] || [ -z "$destination_addr" ] || [ -z "$generat_pkt_size" ] || [ -z "$destination_ifce" ]; then
    echo 'missing -i or -s or -d or -p option' >&2
    echo
    help
    exit 1
fi

sudo hping3 -I $destination_ifce --udp --rand-source --destport $destination_port -V -d $generat_pkt_size -i u1 $destination_addr