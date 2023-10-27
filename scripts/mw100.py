#!/usr/bin/python

import sys
import os
import socket
import time

parent_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(parent_dir)

from constants import MW100_ADDR
from constants import MW100_PORT
from constants import MW100_CHNN

MW100_FORMAT = 'FD0,'+MW100_CHNN+','+MW100_CHNN+'\n'

avg = 0
counter = 0
total = 0

def read_mw100(mw100_addr, mw100_port, mw100_format):
    global avg
    global counter
    global total

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((mw100_addr, mw100_port))

            data = s.recv(1024)
            while 'E0' not in data.decode():
                print("cannot read: waiting E0 flag")
            else:
                counter += 1
                if(counter == 1):
                    print("E0 flag: reading from chanell "+ MW100_CHNN)
                s.sendall(mw100_format.encode())
                time.sleep(1)
                rec = s.recv(1024).decode().split('\n')
                
                read_ene = int(rec[-3].split('\r')[-2].split('+')[-1].split("E")[0])
                read_ene_e = int(rec[-3].split('\r')[-2].split('+')[-1].split("E")[1])
                read_tim = rec[-4].split('\r')[-2]
                read_dat = rec[-5].split('\r')[-2]
                read_ene =  read_ene*(10**read_ene_e)

                total += read_ene
                avg = total / counter
                
                print(read_dat+' '+read_tim+' - counter = '+str(counter)+' - temp = '+str('%.2f'%(read_ene))+' - avg = '+str('%.2f'%(avg))+' - total = '+str('%.2f'%(total)))
    except socket.error as e:
        print("socket error: " %e)
        exit()

while True:
    read_mw100(MW100_ADDR, MW100_PORT, MW100_FORMAT)
