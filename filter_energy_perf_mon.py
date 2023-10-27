#!/usr/bin/python

import zmq
import multiprocessing
import subprocess
from filter_energy_perf_dut import __capture_tty
from constants import SNETIF
from constants import DADDR
from constants import DPORT

context = zmq.Context()

print("Connecting to DUT server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

def __send_packets(size):
    subprocess.run(['./filter_packet_send.sh -i '+ SNETIF +' -d '+ DADDR +' -p '+ DPORT +' -s '+ str(size)], shell=True)

def __measure_mw100():
    subprocess.run(['./scripts/mw100.sh'], shell=True)

for pktSzIt in [16,32,64,128,256,512,1024,1472]:
    sp = multiprocessing.Process(target=__send_packets, args=(pktSzIt,))
    for TestIt in [1,2,3,4,5,6,7,8,9,10]:
        for TestNumIt in [1,2,3,4,5,6,7,8,9]:

            f_out = pktSzIt + '_' + TestIt + '_' + TestNumIt + '_' + 'energy.txt'
            en = multiprocessing.Process(target=__capture_tty, args=(__measure_mw100, f_out))

            en.start()
            print("packet size      : %s" % pktSzIt)
            print("test repetition  : %s" % TestNumIt)
            print("test number      : %s" % TestIt)
            
            request = str(pktSzIt) + "_" + str(TestIt)  + "_" + str(TestNumIt) + "_test"
            print("Sending request: %s" % request)
            socket.send(request.encode())

            message = socket.recv()
            print("Received reply %s [ %s ]" % (request, message))
            
            en.kill()
    sp.kill()