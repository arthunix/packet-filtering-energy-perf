#!/bin/bash

help()
{
   echo "Syntax: packet_filtering_rules_clean [-h | -i interface]"
   echo "options:"
   echo "i     Interface."
   echo "h     Print Help."
   echo
}

while getopts ":hi:" option; do
    case $option in
        h)
            help
            exit;;
        i)
            dIfce=$OPTARG
            ;;
        \?)
            echo "error, invalid option"
            exit;;
    esac
done

if [ -z "$dIfce" ]; then
    echo 'missing -i option' >&2
    echo
    help
    exit 1
fi

echo "=== CLEANING FIREWALL RULES - IPTABLES ==="
sudo iptables -P INPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -P OUTPUT ACCEPT
sudo iptables -t raw -F
sudo iptables -t nat -F
sudo iptables -t mangle -F
sudo iptables -t filter -F
sudo iptables -t security -F
sudo iptables -F
sudo iptables -X
sudo iptables-legacy -P INPUT ACCEPT
sudo iptables-legacy -P FORWARD ACCEPT
sudo iptables-legacy -P OUTPUT ACCEPT
sudo iptables-legacy -t raw -F
sudo iptables-legacy -t nat -F
sudo iptables-legacy -t mangle -F
sudo iptables-legacy -t filter -F
sudo iptables-legacy -t security -F
sudo iptables-legacy -F
sudo iptables-legacy -X
echo "=== FINISHED CLEANING FIREWALL RULES - IPTABLES ==="

echo "=== CLEANING FIREWALL RULES - NFTABLES ==="
sudo nft flush ruleset
echo "=== FINISHED CLEANING FIREWALL RULES - NFTABLES ==="

echo "=== CLEANING FIREWALL RULES - TC ==="
sudo tc qdisc del dev $dIfce root
sudo tc -s qdisc ls dev $dIfce
echo "=== FINISHED CLEANING FIREWALL RULES - TC ==="

echo "=== CLEANING FIREWALL RULES - XDP ==="
sudo xdp-filter unload --all
echo "=== FINISHED CLEANING FIREWALL RULES - XDP ==="