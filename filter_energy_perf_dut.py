#!/usr/bin/python

import time
import zmq
import multiprocessing
import subprocess
import datetime
import logging
from constants import DNETIF
from constants import DADDR
from constants import DPORT
from constants import EXECUTE_FOR_TIME
from constants import EXECUTE_PERF_FOR_TIME

logging.basicConfig(level=logging.INFO)

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

# Abstraction to call function exec the script clean all rules
def __unconfig_rules():
    logging.info('./filter_rules_clean.sh -i '+ DNETIF)
    subprocess.run(['./filter_rules_clean.sh -i '+ DNETIF], shell=True)

# Abstraction to call function exec the script config the rules
# - test 1, 2, 5 and 6 configurure rules on iptables and receive ipaddr, dport
# - test 7, 8, and 9 configurure rules on nftables/tc/xdp respectively and receive ipaddr, dport, ifce
def __configure_rules():
    NUMBER = msg_list[-2]
    
    logging.info('./test_'+ NUMBER +'/config.sh -d '+ DADDR +' -p '+ DPORT)

    if( (int(NUMBER) == 1) or (int(NUMBER) == 2) or (int(NUMBER) == 5) or (int(NUMBER) == 6) ):
        subprocess.run(['./test_'+ NUMBER +'/config.sh -d '+ DADDR +' -p '+ DPORT], shell=True)
    elif( (int(NUMBER) == 7) or (int(NUMBER) == 8) or (int(NUMBER) == 9) ):
        subprocess.run(['./test_'+ NUMBER +'/config.sh -i '+ DNETIF +' -d '+ DADDR +' -p '+ DPORT], shell=True)

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

# just grab all events with perf and save to flamegraph.html
def __grab_flamegraph():
    NUMBER = msg_list[-2]

    if(int(msg_list[-4]) == 16 and int(msg_list[-3]) == 1):
        subprocess.run(['sudo perf script flamegraph -a sleep '+ EXECUTE_PERF_FOR_TIME], shell=True)
        subprocess.run(['mv -f flamegraph.html test_'+ NUMBER +'_flamegraph.html'], shell=True)

# sudo perf script flamegraph -a sleep 30 // send output to perf.data
# sudo bpftrace -e 'profile:hz:99 { @[kstack] = count(); }' > perf.data
# subprocess.run(args, *, stdin=None, input=None, stdout=None, stderr=None, capture_output=False, shell=False, cwd=None, timeout=None, check=False, encoding=None, errors=None, text=None, env=None, universal_newlines=None, **other_popen_kwargs)
# subprocess.Popen(args, bufsize=- 1, executable=None, stdin=None, stdout=None, stderr=None, preexec_fn=None, close_fds=True, shell=False, cwd=None, env=None, universal_newlines=None, startupinfo=None, creationflags=0, restore_signals=True, start_new_session=False, pass_fds=(), *, group=None, extra_groups=None, user=None, umask=- 1, encoding=None, errors=None, text=None, pipesize=- 1, process_group=None)¶
# multiprocessing.Process(target=function, args=()) // start or join

def __test_filter_and_measure():
    # $sudo perf script flamegraph -a sleep 30
    # $sudo timeout 30 test_[TestNum]/filter
    # $sudo timeout 30 test_[TestNum]/measure.sh > [pktSz]_[TestIt]_[TestNum]_measure

    NUMBER = msg_list[-2]
    OUTPUT_F_PREFIX = msg_list[-4] + '_' + msg_list[-3] + '_' + msg_list[-2] + '_'

    cmd_2 = 'sudo timeout ' + EXECUTE_FOR_TIME + ' ./test_'+ NUMBER +'/filter'
    cmd_3 = 'sudo timeout ' + EXECUTE_FOR_TIME + ' ./test_'+ NUMBER +'/measure.sh -f '+ OUTPUT_F_PREFIX + 'measure.txt'
    f_out_2 = OUTPUT_F_PREFIX + 'filter.txt'

    p2 = multiprocessing.Process(target=__capture_tty, args=(cmd_2, f_out_2))
    p3 = multiprocessing.Process(target=__capture_stdout, args=(cmd_3, 'temp'))
    
    p2.start()
    p3.start()
    
    __grab_flamegraph()

    p2.join()
    p3.join()

    subprocess.run(['rm -rf temp'], shell=True)

    time.sleep(1)

def __test_masure():
    # $sudo perf script flamegraph -a sleep 30
    # $sudo timeout 30 test_[TestNum]/measure.sh > [pktSz]_[TestIt]_[TestNum]_measure

    NUMBER = msg_list[-2]
    OUTPUT_F_PREFIX = msg_list[-4] + '_' + msg_list[-3] + '_' + msg_list[-2] + '_'

    cmd_3 = 'sudo timeout ' + EXECUTE_FOR_TIME + ' ./test_'+ NUMBER +'/measure.sh -f ' + OUTPUT_F_PREFIX + 'measure.txt'

    if( (int(msg_list[-2]) == 8) ):
        cmd_3 = cmd_3 + ' -i ' + DNETIF

    __capture_stdout(cmd_3, 'temp')

    subprocess.run(['rm -rf temp'], shell=True)

    __grab_flamegraph()

    time.sleep(1)

def execute_test_1():
    __configure_rules()
    __test_filter_and_measure()
    __unconfig_rules()

def execute_test_2():
    __configure_rules()
    __test_filter_and_measure()
    __unconfig_rules()

def execute_test_3():
    __configure_rules()
    __test_filter_and_measure()
    __unconfig_rules()

def execute_test_4():
    __configure_rules()
    __test_filter_and_measure()
    __unconfig_rules()

def execute_test_5():
    __configure_rules()
    __test_masure()
    __unconfig_rules()

def execute_test_6():
    __configure_rules()
    __test_masure()
    __unconfig_rules()

def execute_test_7():
    __configure_rules()
    __test_masure()
    __unconfig_rules()

def execute_test_8():
    __configure_rules()
    __test_masure()
    __unconfig_rules()

def execute_test_9():
    __configure_rules()
    __test_masure()
    __unconfig_rules()

if __name__ == '__main__':
    timedate_stamp = str(datetime.datetime.now())
    folder_prefix = timedate_stamp.split(' ')[0] + '-' + timedate_stamp.split(' ')[1].split(':')[0] + '-' + timedate_stamp.split(' ')[1].split(':')[1]
    subprocess.run(['mkdir measures/'+folder_prefix+'/'], shell=True)

    while True:
        message = socket.recv()
        print("Received request: %s" % message)

        msg_list = message.decode().split("_")
        print("packet size      : %s" % msg_list[-4])
        print("test repetition  : %s" % msg_list[-3])
        print("test number      : %s" % msg_list[-2])
        
        match int(msg_list[-2]):
            case 1:
                execute_test_1()
            case 2:
                execute_test_2()
            case 3:
                execute_test_3()
            case 4:
                execute_test_4()
            case 5:
                execute_test_5()
            case 6:
                execute_test_6()
            case 7:
                execute_test_7()
            case 8:
                execute_test_8()
            case 9:
                execute_test_9()

        subprocess.run(['mv -f *_measure.txt measures/'+folder_prefix+'/'], shell=True)
        subprocess.run(['mv -f *_filter.txt measures/'+folder_prefix+'/'], shell=True)
        #subprocess.run(['mv -f *_energy.txt measures/'+folder_prefix+'/'], shell=True)
        subprocess.run(['mv -f *.html measures/'+folder_prefix+'/'], shell=True)

        socket.send(message + "_done".encode())
