from hcal_teststand import *
from hcal_teststand.hcal_teststand import teststand
import sys
import random
import os
from fnmatch import fnmatch

def check_power(ts):
    print "**********************************"
    print "Checking backplane power status..."
    print "**********************************"
    
    results = ngccm.send_commands_parsed( ts, "get HF2-bkp_pwr_bad")
    if results['output'][0]['result'] == "1":
        print "************************************************"
        print "Backplane power off. Attempting to turn it on..."
        print "************************************************"
        results = ngccm.send_commands_parsed( ts, "put HF2-bkp_pwr_enable 1")
        if results['output'][0]['result'] == "OK":
            print "***************************"
            print "Power enabled. Verifying..."
            print "***************************"
            results = ngccm.send_commands_parsed( ts, "get HF2-bkp_pwr_bad")
            if results['output'][0]['result'] == "0":
                print "************************"
                print "Power verified. Proceed."
                print "************************"
                return 0
            else:
                print "************************************"
                print "Something has gone wrong. Try again."
                print "************************************"
                return 1
        else:
            print "************************************"
            print "Something has gone wrong. Try again."
            print "************************************"
            return 1
    else:
        print "************************"
        print "The power status is good"
        print "************************"
        return 0

def TestAll(ts, verbose, max_bits, QIE_slot_number):
    print "*************************************"
    print "Testing registers on all QIE chips..."
    print "*************************************"

    reg_file = open('QIE_registers')
    reginf = reg_file.readlines()
    reg_file.close()

    registers = []
    bits = []
    for i in range(0,len(reginf)):
        registers.append(reginf[i].split(':')[0].rstrip())
        bits.append(reginf[i].split(':')[1].rstrip())

    GLIB_slot_number = 2
#    QIE_slot_number = 2

    random.seed()

    regadd = []
    commands = []
    expect = []
    for i in range(0,len(reginf)):
        regadd = "HF" + str(GLIB_slot_number) + "-" + str(QIE_slot_number) + "-QIE[1-24]_" + registers[i]
        if int(bits[i]) > max_bits:
            for k in range(0,2**int(max_bits)):
                l = random.randint(0,(2**int(bits[i]))-1)
                commands.append("put " + regadd + " 24*" + str(l))
                commands.append("get " + regadd)
                if l > 9:
                    l = hex(l)
                expect.append((24*(str(l) + " ")).rstrip())
        else:
            for j in range(0,2**int(bits[i])):
                commands.append("put " + regadd + " 24*" + str(j))
                commands.append("get " + regadd)
                if j > 9:
                    j = hex(j)
                expect.append((24*(str(j) + " ")).rstrip())

    results = ngccm.send_commands_parsed(ts, commands)

    write_failures = []
    read_failures = []
    both_failures = []
    read_failures_array = []
    for i in range(0,len(results['output'])/2):
        if (results['output'][2*i]['result'] == "OK") and (results['output'][(2*i)+1]['result'] == expect[i]):
            if verbose == 1:
                print "Success! Command: " + results['output'][2*i]['cmd'] + ", Returned: " + results['output'][(2*i)+1]['result']
        elif results['output'][(2*i)+1]['result'] == expect[i]:
            if verbose == 1:
                print "Write failure! Command: " + results['output'][2*i]['cmd'] + ", Returned: " + results['output'][2*i]['result']
            write_failures.append("Command: " + results['output'][2*i]['cmd'] + ", Returned: " + results['output'][2*i]['result'])
        elif results['output'][2*i]['result'] == "OK":
            if verbose == 1:
                print "Read Failure! Command: " + results['output'][2*i]['cmd'] + ", Returned: " + results['output'][(2*i)+1]['result']
            read_failures.append("Command: " + results['output'][2*i]['cmd'] + ", Returned: " + results['output'][(2*i)+1]['result'])
            read_failures_array.append(results['output'][(2*i)+1]['result'])
        else:
            if verbose ==1:
                print "Write and read failure!"
                print "     WRITE: Command: " + results['output'][2*i]['cmd'] + ", Returned: " + results['output'][2*i]['result']
                print "     READ: Command: " + results['output'][2*i]['cmd'] + ", Returned: " + results['output'][(2*i)+1]['result']
            both_failures.append("Command: " + results['output'][2*i]['cmd'] + ", " + "Write output: " + results['output'][2*i]['result']+ ", Read output: " + results['output'][(2*i)+1]['result'])

    if (len(write_failures) + len(read_failures) + len(both_failures)) == 0:
        print "**************************************"
        print "All QIE registers tested successfully."
        print "**************************************"
        return 0,0,0,[]
    else:
        print "*********************************************************"
        print "There were some failures while testing the QIE registers."
        print "*********************************************************"
        print "There were " + str(len(write_failures)) + " write failures."
        for failure in write_failures:
            print "     " + failure
        print "There were " + str(len(read_failures)) + " read failures."
        for failure in read_failures:
            print "     " + failure
        print "There were " + str(len(both_failures)) + " write and read failures."
        for failure in both_failures:
            print "     " + failure
        print "*********************************************************"
        return len(write_failures), len(read_failures), len(both_failures), read_failures_array

def TestOne(ts, verbose, max_bits, QIE_slot_number, QIE_chip_number):

    print "***************************************"
    print "Testing registers on QIE chip " + str(QIE_chip_number) + "..."
    print "***************************************"

    reg_file = open('QIE_registers')
    reginf = reg_file.readlines()
    reg_file.close()

    registers = []
    bits = []
    for i in range(0,len(reginf)):
        registers.append(reginf[i].split(':')[0].rstrip())
        bits.append(reginf[i].split(':')[1].rstrip())

    GLIB_slot_number = 2
#    QIE_slot_number = 2
#    QIE_chip_number = 1

    random.seed()

    regadd = []
    commands = []
    expect = []
    for i in range(0,len(reginf)):
        regadd = "HF" + str(GLIB_slot_number) + "-" + str(QIE_slot_number) + "-QIE" + str(QIE_chip_number) + "_" + registers[i]
        if int(bits[i]) > max_bits:
            for k in range(0,2**int(max_bits)):
                l = random.randint(0,(2**int(bits[i]))-1)
                commands.append("put " + regadd + " " + str(l))
                commands.append("get " + regadd)
                if l > 9:
                    l = hex(l)
                expect.append(str(l).rstrip())
        else:
            for j in range(0,2**int(bits[i])):
                commands.append("put " + regadd + " " + str(j))
                commands.append("get " + regadd)
                if j > 9:
                    j = hex(j)
                expect.append(str(j).rstrip())

    results = ngccm.send_commands_parsed(ts, commands)

    write_failures = []
    read_failures = []
    both_failures = []
    read_failures_array = []
    for i in range(0,len(results['output'])/2):
        if (results['output'][2*i]['result'] == "OK") and (results['output'][(2*i)+1]['result'] == expect[i]):
            if verbose == 1:
                print "Success! Command: " + results['output'][2*i]['cmd'] + ", Returned: " + results['output'][(2*i)+1]['result']
        elif results['output'][(2*i)+1]['result'] == expect[i]:
            if verbose == 1:
                print "Write failure! Command: " + results['output'][2*i]['cmd'] + ", Returned: " + results['output'][2*i]['result']
            write_failures.append("Command: " + results['output'][2*i]['cmd'] + ", Returned: " + results['output'][2*i]['result'])
        elif results['output'][2*i]['result'] == "OK":
            if verbose == 1:
                print "Read Failure! Command: " + results['output'][2*i]['cmd'] + ", Returned: " + results['output'][(2*i)+1]['result']
            read_failures.append("Command: " + results['output'][2*i]['cmd'] + ", Returned: " + results['output'][(2*i)+1]['result'])
            read_failures_array.append(results['output'][(2*i)+1]['result'])
        else:
            if verbose ==1:
                print "Write and read failure!"
                print "     WRITE: Command: " + results['output'][2*i]['cmd'] + ", Returned: " + results['output'][2*i]['result']
                print "     READ: Command: " + results['output'][2*i]['cmd'] + ", Returned: " + results['output'][(2*i)+1]['result']
            both_failures.append("Command: " + results['output'][2*i]['cmd'] + ", " + "Write output: " + results['output'][2*i]['result']+ ", Read output: " + results['output'][(2*i)+1]['result'])

    if (len(write_failures) + len(read_failures) + len(both_failures)) == 0:
        print "************************************************************"
        print "All registers tested successfully on QIE chip " + str(QIE_chip_number) + "."
        print "************************************************************"
        return 0,0,0,[]
    else:
        print "************************************************************"
        print "There were some failures while testing QIE chip " + str(QIE_chip_number) + "."
        print "************************************************************"
        print "There were " + str(len(write_failures)) + " write failures."
        for failure in write_failures:
            print "     " + failure
        print "There were " + str(len(read_failures)) + " read failures."
        for failure in read_failures:
            print "     " + failure
        print "There were " + str(len(both_failures)) + " write and read failures."
        for failure in both_failures:
            print "     " + failure
        print "*********************************************************"
        return len(write_failures), len(read_failures), len(both_failures), read_failures_array
