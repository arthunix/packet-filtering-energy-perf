#!/usr/bin/python

import zmq
import multiprocessing
import subprocess
import datetime
from filter_energy_perf_dut import __capture_tty

context = zmq.Context()

print("Connecting to DUT server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

EXECUTE_FOR_TIME = '30'     # in seconds
EXECUTE_PERF_FOR_TIME = '5' # in seconds

DNETIF = 'enp5s0f0'
SNETIF = 'enp5s0f1'
DADDR = '127.0.0.1'
SADDR = '127.0.0.1'
DPORT = '12345'
SPORT = '12345'

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