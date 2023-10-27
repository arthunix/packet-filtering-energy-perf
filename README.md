# packet filtering energy perf framework

## requeriments
- `python 3.11 or above`
- `linux-perf`
- `iptables`
- `nftables`
- `libbpf` and `libxdp`
- `bpftrace`
- `xdp-tools`
- `ZeroMQ`

- `Flamegraph` Available: `https://github.com/brendangregg/FlameGraph`
- `perf-script` Available on folder: `/usr/lib/perf-core/scripts/python/flamegraph.py`

```sh
# download template file used by the perf to create the flamegraph, should exit a deb packet but there is no
sudo mkdir /usr/share/d3-flame-graph/
sudo wget -O /usr/share/d3-flame-graph/d3-flamegraph-base.html https://cdn.jsdelivr.net/npm/d3-flame-graph@4/dist/templates/d3-flamegraph-base.html
```
You need to fix the parameters in the files `constants.py` and `scripts/constants.py`
```py
MW100_ADDR = '192.168.0.10'
MW100_PORT = 34318
MW100_CHNN = '7'
EXECUTE_FOR_TIME = '5'      # in seconds
EXECUTE_PERF_FOR_TIME = '5' # in seconds
DNETIF = 'enp5s0f0'
SNETIF = 'enp5s0f1'
DADDR = '127.0.0.1'
SADDR = '127.0.0.1'
DPORT = '12345'
SPORT = '12345'
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
                libbpf-dev sysstat xdp-tools tcpdump linux-perf iproute2 bpftrace python3-zmq -y
sudo apt autoremove && sudo apt clean && sudo apt autoclean -y
```

## install on Debian 12 Bookworm armv7l GNU/Linux (Raspberry Pi OS)
```sh
sudo apt update && sudo apt upgrade -y
sudo apt install raspberrypi-kernel-headers -y
sudo apt install build-essential clang llvm git libc6-dev libelf-dev m4 libpcap-dev   \
                iperf3 hping3 python3 python-is-python3 binutils-dev pkg-config wget  \
                libbpf-dev sysstat xdp-tools tcpdump linux-perf iproute2 python3-zmq -y
sudo apt autoremove && sudo apt clean && sudo apt autoclean -y
```

## install on Ubuntu 20.04 LTS x86_64 GNU/Linux
```sh
sudo apt update && sudo apt upgrade -y
sudo apt install linux-headers-$(uname -r) -y
# xdp-tools not available, just for Ubuntu Mantic, Lunar and Kinetic
sudo apt install build-essential clang llvm git libc6-dev libelf-dev m4 libpcap-dev      \
                 iperf3 hping3 iproute2 bpftrace python3 python-is-python3 binutils-dev  \
                 pkg-config wget libbpf-dev sysstat tcpdump linux-tools-common           \
                 python3-zmq linux-tools-generic linux-tools-$(uname -r) -y
sudo apt autoremove && sudo apt clean && sudo apt autoclean -y
wget https://github.com/xdp-project/xdp-tools/releases/download/v1.4.0/xdp-tools-1.4.0.tar.gz
tar -xvf xdp-tools-1.4.0
./configure
make && sudo make install
```

## TEST EXPLANATION:
### test 1: filter at userspace with tracking (conntrack)
```sh
# guarantees that packet not drop
sudo iptables -I PREROUTING -t raw    -d $dAddr -p udp --dport $dPort -j ACCEPT
sudo iptables -I INPUT      -t filter -d $dAddr -p udp --dport $dPort -j ACCEPT
```
```sh
sudo iptables -L -v -n -t raw >> $fName && sudo iptables -L -v -n -t filter >> $fName && mpstat -u -I SUM -P ALL 1 1 | grep -E -v Aver >> $fName
```
### test 2: filter at userspace without tracking (no conntrack)
```sh
# guarantees that packet not drop
sudo iptables -I PREROUTING -t raw    -d $dAddr -p udp --dport $dPort -j NOTRACK
sudo iptables -I INPUT      -t filter -d $dAddr -p udp --dport $dPort -j ACCEPT
```
```sh
sudo iptables -L -v -n -t raw >> $fName && sudo iptables -L -v -n -t filter >> $fName && mpstat -u -I SUM -P ALL 1 1 | grep -E -v Aver >> $fName
```
### test 3: filter at socket (bpf: berkeley packet filter)
```C
struct sock_filter code[] = {
	{ 0x28, 0, 0, 0x0000000c },
	{ 0x15, 0,10, 0x00000800 },
	{ 0x20, 0, 0, 0x0000001e },
	{ 0x15, 0, 8, 0xc0a8004f },
	{ 0x30, 0, 0, 0x00000017 },
	{ 0x15, 0, 6, 0x00000011 },
	{ 0x28, 0, 0, 0x00000014 },
	{ 0x45, 4, 0, 0x00001fff },
	{ 0xb1, 0, 0, 0x0000000e },
	{ 0x48, 0, 0, 0x00000010 },
	{ 0x15, 0, 1, 0x00003039 },
	{ 0x6,  0, 0, 0x00040000 },
	{ 0x6,  0, 0, 0x00000000 },
};
```
```sh
sudo mpstat -u -I SUM -P ALL 1 1 | grep -E -v Aver >> $fName
```
### test 4: filter at socket (ebpf: extended berkeley packet filter)
```C
0000000000000000 <socket_filter>:
       0:       71 12 17 00 00 00 00 00 r2 = *(u8 *)(r1 + 0x17)
       1:       55 02 05 00 11 00 00 00 if r2 != 0x11 goto +0x5 <LBB0_3>
       2:       61 12 1e 00 00 00 00 00 r2 = *(u32 *)(r1 + 0x1e)
       3:       55 02 03 00 c0 a8 00 4f if r2 != 0x4f00a8c0 goto +0x3 <LBB0_3>
       4:       b7 00 00 00 01 00 00 00 r0 = 0x1
       5:       69 11 24 00 00 00 00 00 r1 = *(u16 *)(r1 + 0x24)
       6:       15 01 01 00 30 39 00 00 if r1 == 0x3930 goto +0x1 <LBB0_4>
```
```sh
sudo mpstat -u -I SUM -P ALL 1 1 | grep -E -v Aver >> $fName
```
### test 5: filter at kernel netfilter (iptables input chain)
```sh
sudo iptables-legacy -I PREROUTING -t raw -d $dAddr -p udp --dport $dPort -j DROP
```
```sh
sudo iptables -L -v -n -t raw >> $fName && sudo iptables -L -v -n -t filter >> $fName && mpstat -u -I SUM -P ALL 1 1 | grep -E -v Aver >> $fName
```
### test 6: filter at kernel netfilter (iptables pre-routing chain)
```sh
sudo iptables-legacy -I PREROUTING -t raw    -d $dAddr -p udp --dport $dPort -j NOTRACK
sudo iptables-legacy -I INPUT      -t filter -d $dAddr -p udp --dport $dPort -j DROP
```
```sh
sudo iptables -L -v -n -t raw >> $fName && sudo iptables -L -v -n -t filter >> $fName && mpstat -u -I SUM -P ALL 1 1 | grep -E -v Aver >> $fName
```
### test 7: filter at kernel netfilter (nftables ingress)
```sh
sudo nft add table netdev filter
sudo nft 'add chain netdev filter input { type filter hook ingress device '$iFace' priority -500 ; policy accept ; }'
sudo nft 'add rule netdev filter input ip daddr '$dAddr' udp dport '$dPort' counter drop'
```
```sh
sudo nft --handle list chain netdev filter input >> $fName && mpstat -u -I SUM -P ALL 1 1 | grep -E -v Aver >> $fName
```
### test 8: filter at kernel scheduling (traffic control - tc)
```sh
sudo tc qdisc add dev $iFace ingress
sudo tc filter add dev $iFace parent ffff: prio 4 protocol ip u32 match ip protocol 17 0xff match ip dport $dPort 0xffff match ip dst $dAddr flowid 1:1 action drop
```
```sh
sudo tc -s filter show dev $iFace ingress >> $fName && mpstat -u -I SUM -P ALL 1 1 | grep -E -v Aver >> $fName
```
### test 9: filter at kernel device driver (xdp - express data path)
```sh
sudo xdp-filter load -m skb $iFace
sudo xdp-filter ip $dAddr -m dst
sudo xdp-filter port -m dst $dPort -p udp
```
```sh
sudo xdp-filter status >> $fName && mpstat -u -I SUM -P ALL 1 1 | grep -E -v Aver >> $fName
```

## bpftrace (don't work in raspberry armv7l)
```sh
# sudo bpftrace -o perf-bpftrace.perf -e 'kprobe:napi_gro_receive { @[kstack] = count(); }'
bpftrace -e 'profile:hz:99 { @[kstack] = count(); }'
./scripts/stackcollapse-bpftrace.pl perf-bpftrace.perf > perf-bpftrace.foled
./scripts/flamegraph.pl perf-bpftrace.foled > perf-bpftrace.svg
```