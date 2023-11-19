FROM ubuntu:mantic

LABEL maintainer="Arthur Silverio <thursilverio@gmail.com>"

RUN apt update && apt upgrade -y
RUN apt install linux-headers-$(uname -r) -y
RUN apt install build-essential clang llvm git libc6-dev libelf-dev m4 libpcap-dev          \
                iperf3 hping3 iproute2 bpftrace python3 python-is-python3 binutils-dev      \
                pkg-config wget libbpf-dev sysstat tcpdump linux-tools-common nftables      \
                libbpf-dev sysstat tcpdump iproute2 bpftrace python3-zmq iptables psmisc    \
                python3-zmq sudo xdp-tools linux-tools-generic linux-tools-$(uname -r) -y
RUN apt autoremove && apt clean && apt autoclean -y

# docker run --rm -it --cap-add=NET_ADMIN --cap-add=BPF -v ${PWD}:/root ubuntu:mantic /bin/bash
# docker run --rm -it --cap-add=NET_ADMIN --cap-add=BPF -v ${PWD}:/root perf /bin/bash

# iperf3 -c 172.17.0.2 -p 6970 -u --get-server-output --bidir
# iperf3 -c 172.17.0.2 -p 6970 -u --get-server-output
# iperf3 -s -p 6970