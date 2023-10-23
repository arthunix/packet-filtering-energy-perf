# packet filtering energy perf framework

## requeriments
- `python 3.11 or above`
- `linux-perf`
- `iptables`
- `nftables`
- `libbpf` and `libxdp`
- `bpftrace`
- `xdp-tools`

- `Flamegraph` Available: `https://github.com/brendangregg/FlameGraph`
- `perf-script` Available on folder: `/usr/lib/perf-core/scripts/python/flamegraph.py`

```sh
# download template file used by the perf to create the flamegraph, should exit a deb packet but there is no
sudo mkdir /usr/share/d3-flame-graph/
sudo wget -O /usr/share/d3-flame-graph/d3-flamegraph-base.html https://cdn.jsdelivr.net/npm/d3-flame-graph@4/dist/templates/d3-flamegraph-base.html
```
```sh
# there is a script capture mw100 reads, it is proprietary, I don´t have author autorization to publish
https://github.com/arthunix/scripts
https://github.com/arthunix/scripts/blob/main/measure_mw100
```

## tested on
- `Ubuntu 20.04 LTS x86_64 GNU/Linux`
- `Debian 12 Bookworm x86_64 GNU/Linux`
- `Debian 12 Bookworm armv7l GNU/Linux (Raspberry Pi OS)`

## install on Debian 12 Bookworm x86_64 GNU/Linux
```sh
sudo apt update && sudo apt upgrade -y
sudo apt install linux-headers-$(uname -r) -y
sudo apt install build-essential clang llvm git libc6-dev libelf-dev m4 libpcap-dev   \
                iperf3 hping3 python3 python-is-python3 binutils-dev pkg-config wget  \
                libbpf-dev sysstat xdp-tools tcpdump linux-perf iproute2 bpftrace -y
sudo apt autoremove && sudo apt clean && sudo apt autoclean -y
```

## install on Debian 12 Bookworm armv7l GNU/Linux (Raspberry Pi OS)

## install on Ubuntu 20.04 LTS x86_64 GNU/Linux
```sh
sudo apt update && sudo apt upgrade -y
sudo apt install linux-headers-$(uname -r) -y
# xdp-tools not available, just for Ubuntu Mantic, Lunar and Kinetic
sudo apt install build-essential clang llvm git libc6-dev libelf-dev m4 libpcap-dev      \
                 iperf3 hping3 iproute2 bpftrace python3 python-is-python3 binutils-dev  \
                 pkg-config wget libbpf-dev sysstat tcpdump linux-tools-common           \
                 linux-tools-generic linux-tools-$(uname -r) -y
sudo apt autoremove && sudo apt clean && sudo apt autoclean -y
wget https://github.com/xdp-project/xdp-tools/releases/download/v1.4.0/xdp-tools-1.4.0.tar.gz
tar -xvf xdp-tools-1.4.0
./configure
make && sudo make install
```

## TEST EXPLANATION:
### test 1: filter at userspace with tracking (conntrack)
### test 2: filter at userspace without tracking (no conntrack)
### test 3: filter at socket (bpf: berkeley packet filter)
### test 4: filter at socket (ebpf: extended berkeley packet filter)
### test 5: filter at kernel netfilter (iptables input chain)
### test 6: filter at kernel netfilter (iptables pre-routing chain)
### test 7: filter at kernel netfilter (nftables ingress)
### test 8: filter at kernel scheduling (traffic control - tc)
### test 9: filter at kernel device driver (xdp - express data path)

