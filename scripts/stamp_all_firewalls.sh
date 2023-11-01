#!/bin/bash

sudo iptables -L -v -n -t raw && sudo iptables -L -v -n -t filter
sudo iptables-legacy -L -v -n -t raw && sudo iptables-legacy -L -v -n -t filter
sudo nft --handle list chain netdev filter input
sudo tc -s filter show dev eth0 ingress
sudo tc -s qdisc show dev eth0 ingress
sudo xdp-filter status