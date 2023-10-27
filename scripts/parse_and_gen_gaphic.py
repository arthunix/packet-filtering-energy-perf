#!/usr/bin/python

# [pktSz]_[TestIt]_[TestNum]_filter
# [pktSz]_[TestIt]_[TestNum]_energy
# [pktSz]_[TestIt]_[TestNum]_measure

import os
import subprocess
import matplotlib.pyplot as plt
import numpy as np

def __read_content_from_files_with(folder, pattern_pkt_size, pattern_test_num):
    file_contents = {}
    for root, _, files in os.walk(folder):
        for file in files:
            if (file.find(pattern_pkt_size) >= 0) and (file.find(pattern_test_num) >= 0):
                path = os.path.join(root, file)
                with open(path, 'r') as f:
                    file_contents[file] = f.readlines()
    return file_contents

def __extract_energy_content(file_contents):
    # DATE 23/10/27 TIME 14:24:13 - counter = 1 - temp = 2.50 - avg = 2.50 - total = 2.50
    value = 0
    counter = 0

    for file, lines in file_contents.items():
        for line in lines:
            #print(line)
            try:
                parts = line.split()[-5]
                value += float(parts[-1])
                counter += 1
            except ValueError:
                pass
            except IndexError:
                pass

    if counter > 0:
        return value / counter
    else:
        return 0
    
def __extract_cpu_content(file_contents):
    # 01:27:13 PM  CPU    %usr   %nice    %sys %iowait    %irq   %soft  %steal  %guest  %gnice   %idle
    # 01:27:14 PM  all   21.71    0.00    2.51    6.02    0.00    0.00    0.00    0.00    0.00   69.76
    value = 0
    counter = 0

    for file, lines in file_contents.items():
        for line in lines:
            #print(line)
            parts = line.split()
            try:
                if(parts[2] == 'all'):
                    value += float(parts[-1])
                    counter += 1
            except ValueError:
                pass
            except IndexError:
                pass

    if counter > 0:
        return value / counter
    else:
        return 0

def __extract_filter_content(file_contents):
    value = 0
    counter = 0

FOLDER = "../measures/2023-10-27-13-26/"

if __name__ == '__main__':
    energy = dict.fromkeys(['16','32','64','128','256','512','1024','1472'], { '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0, '9': 0} )
    cpu = dict.fromkeys(['16','32','64','128','256','512','1024','1472'], { '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0, '9': 0} )
    filter = dict.fromkeys(['16','32','64','128','256','512','1024','1472'], { '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0, '9': 0} )

    for pktSzIt in [16,32,64,128,256,512,1024,1472]:
        for TestNumIt in [1,2,3,4,5,6,7,8,9]:
            file_contents = __read_content_from_files_with(FOLDER, str(TestNumIt)+'_energy.txt', str(pktSzIt))
            energy[str(pktSzIt)][str(TestNumIt)] = __extract_energy_content(file_contents)

            file_contents = __read_content_from_files_with(FOLDER, str(TestNumIt)+'_measure.txt', str(pktSzIt))
            cpu[str(pktSzIt)][str(TestNumIt)] = __extract_cpu_content(file_contents)

            #file_contents = __read_content_from_files_with(FOLDER, str(TestNumIt)+'_filter.txt', str(pktSzIt))
            #filter[str(pktSzIt)][str(TestNumIt)] = __extract_filter_content(file_contents)

    for pktSzIt in [16,32,64,128,256,512,1024,1472]:
        
        energy_range = energy[str(pktSzIt)].keys()
        energy_range_val = energy[str(pktSzIt)].values()
        cpu_range = cpu[str(pktSzIt)].keys()
        cpu_range_val = cpu[str(pktSzIt)].values()

        range_tests = ['userspace', 'userspace no conntrack', 'bpf', 'ebpf', 'iptables pre routing', 'iptables input', 'nftables ingress', 'tc', 'xdp']

        fig, ax = plt.subplots()
        ax.bar(range_tests, energy_range_val)
        ax.set(xlabel='filter', ylabel='watts (W)', title='')
        fig.set_figwidth(20)
        fig.savefig(str(pktSzIt) + '_' + "energy.png")

        fig, ax = plt.subplots()
        ax.bar(range_tests, cpu_range_val)
        ax.set(xlabel='filter', ylabel='watts (W)', title='About as simple as it gets, folks')
        fig.set_figwidth(20)
        fig.savefig(str(pktSzIt) + '_' + "cpu.png")
            
    subprocess.run(['mv -f *.png '+FOLDER], shell=True)
    #print(energy)
    #print(cpu)
    #print(filter)

