#!/usr/bin/python

# [pktSz]_[TestIt]_[TestNum]_filter
# [pktSz]_[TestIt]_[TestNum]_energy
# [pktSz]_[TestIt]_[TestNum]_measure

import os
import subprocess
import logging
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.WARNING)

def __read_content_from_files_with(folder, pattern_pkt_size, pattern_test_num):
    logging.info("init: __read_content_from_files_with")
    file_contents = {}
    for root, _, files in os.walk(folder):
        for file in files:
            if (file.find(pattern_pkt_size) >= 0) and (file.find(pattern_test_num) >= 0):
                path = os.path.join(root, file)
                logging.info("file: " + file)
                with open(path, 'r') as f:
                    file_contents[file] = f.readlines()
    return file_contents

def __extract_energy_content(file_contents):
    # DATE 23/10/27 TIME 14:24:13 - counter = 1 - temp = 2.50 - avg = 2.50 - total = 2.50
    logging.info("init: __extract_energy_content")
    value = 0
    counter = 0

    for file, lines in file_contents.items():
        for line in lines:
            parts = line.split()
            logging.info(line)
            logging.info(parts)
            try:
                parts = line.split()[-5]
                value += float(parts[-1])
                counter += 1
                logging.info("value: %i" %(value))
                logging.info("counter: %i" %(counter))
            except ValueError:
                pass
            except IndexError:
                pass

    if counter > 0:
        logging.info("returning: %f" %(value/counter))
        return value / counter
    else:
        logging.info("returning: 0")
        return 0
    
def __extract_cpu_content(file_contents):
    # 01:27:13 PM  CPU    %usr   %nice    %sys %iowait    %irq   %soft  %steal  %guest  %gnice   %idle
    # 01:27:14 PM  all   21.71    0.00    2.51    6.02    0.00    0.00    0.00    0.00    0.00   69.76
    logging.info("init: __extract_cpu_content")
    value = 0
    counter = 0

    for file, lines in file_contents.items():
        for line in lines:
            parts = line.split()
            try: 
                if(parts[1] == 'all' and len(parts) > 3):
                    logging.info(line)
                    value += float(parts[-1])
                    counter += 1
                    logging.info("value: %i" %(value))
                    logging.info("counter: %i" %(counter))
            except ValueError:
                pass
            except IndexError:
                pass
    
    if counter > 0:
        logging.info("returning: %f" %(value/counter))
        return 100 - (value/counter)
    else:
        logging.info("returning: 0")
        return 0

def __extract_filter_content(file_contents):
    logging.info("init: __extract_filter_content")
    value = 0
    counter = 0

FOLDER = "measures/2023-10-27-17-42/"

if __name__ == '__main__':
    pkt_keys = ['16','32','64','128','256','512','1024','1472']
    tst_keys = ['1','2','3','4','5','6','7','8','9']

    ene = {pkt_keys: {tst_keys: 0.0 for tst_keys in tst_keys} for pkt_keys in pkt_keys}
    cpu = {pkt_keys: {tst_keys: 0.0 for tst_keys in tst_keys} for pkt_keys in pkt_keys}
    flt = {pkt_keys: {tst_keys: 0.0 for tst_keys in tst_keys} for pkt_keys in pkt_keys}

    for pktSzIt in [16,32,64,128,256,512,1024,1472]:
        for TestNum in [1,2,3,4,5,6,7,8,9]:
            logging.info("pkt size: %i, test num: %i" % (pktSzIt, TestNum) )

            file_contents = __read_content_from_files_with(FOLDER, str(TestNum)+'_energy.txt', str(pktSzIt))
            ene[str(pktSzIt)][str(TestNum)] = __extract_energy_content(file_contents)
            
            file_contents = __read_content_from_files_with(FOLDER, str(TestNum)+'_measure.txt', str(pktSzIt))
            cpu[str(pktSzIt)][str(TestNum)] = __extract_cpu_content(file_contents)

            #file_contents = __read_content_from_files_with(FOLDER, str(TestNumIt)+'_filter.txt', str(pktSzIt))
            #filter[str(pktSzIt)][str(TestNumIt)] = __extract_filter_content(file_contents)

    for pktSzIt in [16,32,64,128,256,512,1024,1472]:
        #energy_range = energy[str(pktSzIt)].keys()
        energy_range_val = ene[str(pktSzIt)].values()
        #cpu_range = cpu[str(pktSzIt)].keys()
        cpu_range_val = cpu[str(pktSzIt)].values()

        range_tests = ['userspace', 'userspace no conntrack', 'bpf', 'ebpf', 'iptables pre routing', 'iptables input', 'nftables ingress', 'tc', 'xdp']

        fig, ax = plt.subplots()
        ax.bar(range_tests, energy_range_val)
        ax.set(xlabel='filter type', ylabel='watts (W)', title='Energy Consumption Comparative Analysis for a '+ str(pktSzIt) +' bytes packet')
        fig.set_figwidth(20)
        fig.savefig(str(pktSzIt) + '_' + "energy.png")

        fig, ax = plt.subplots()
        ax.bar(range_tests, cpu_range_val)
        ax.set(xlabel='filter type', ylabel='cpu consumption (%)', title='Resources Consumption Comparative Analysis for a '+ str(pktSzIt) +' bytes packet')
        fig.set_figwidth(20)
        fig.savefig(str(pktSzIt) + '_' + "cpu.png")
            
    subprocess.run(['mv -f *.png '+FOLDER], shell=True)
    logging.info(ene)
    logging.info(cpu)
    logging.info(flt)
