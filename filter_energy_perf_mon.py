#!/usr/bin/python

import zmq
import multiprocessing
import subprocess
from constants import SNETIF
from constants import DADDR
from constants import DPORT
from constants import EXECUTE_FOR_TIME

context = zmq.Context()

print("Connecting to DUT server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

def __send_packets(size):
    subprocess.run(['./filter_packet_send.sh -i '+ SNETIF +' -d '+ DADDR +' -p '+ DPORT +' -s '+ str(size)], shell=True)

# Abstraction to procedure to capture scripts written to tty (should work with watch and mmwatch, but is horrendous)
def __capture_tty(command, out):
    subprocess.run(['script', '-q', '-c', command, '/tmp/output_typescript'])
    with open('/tmp/output_typescript', 'r') as f:
        output = f.read()
    with open(out, 'w') as f:
        f.write(output)
    subprocess.run(['rm', '/tmp/output_typescript'])

# Abstraction to procedure to capture scripts written to stdout
def __capture_stdout(command, out):
    with open(out, 'w') as f:
        subprocess.run([command], stdout=f, shell=True)

if __name__ == '__main__':
    for pktSzIt in [16,32,64,128,256,512,1024,1472]:
        sp = multiprocessing.Process(target=__send_packets, args=(pktSzIt,))
        for TestIt in [1,2,3,4,5,6,7,8,9,10]:
            for TestNumIt in [1,2,3,4,5,6,7,8,9]:

                f_out = str(pktSzIt) + '_' + str(TestIt) + '_' + str(TestNumIt) + '_' + 'energy.txt'
                en = multiprocessing.Process(target=__capture_tty, args=('sudo timeout ' + EXECUTE_FOR_TIME + ' ./scripts/mw100.py', f_out))

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