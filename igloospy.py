from hcal_teststand import *
from hcal_teststand.hcal_teststand import teststand
import sys
crate=1
slot=10
if __name__=="__main__":
    	name = ""
	if len(sys.argv) == 1:
		name = "904"
	elif len(sys.argv) == 2:
		name = sys.argv[1]
	else:
		name = "904"
	ts = teststand(name)		# Initialize a teststand object. This object stores the teststand configuration and has a number of useful methods.
        fl=open('iglooout.txt','w')
        command1=['put HF{0}-{1}-iTop_CntrReg 0x2'.format(crate,slot),'put HF{0}-{1}-iTop_CntrReg 0x0'.format(crate,slot)]
        command2=['get HF{0}-{1}-iTop_StatusReg'.format(crate,slot),'get HF{0}-{1}-iTop_inputSpy'.format(crate,slot)]*512
        command1.extend(command2)
        outp=ngccm.send_commands_parsed(ts,command1)['output']
        for opt in outp:
            if opt['cmd'] == 'put HF{0}-{1}-iTop_CntrReg 0x2'.format(crate,slot):
                if opt['result']=='OK':
                    continue
                else:
                    print 'ERROR'
                    exit()
            if opt['cmd'] == 'put HF{0}-{1}-iTop_CntrReg 0x0'.format(crate,slot):
                if opt['result']=='OK':
                    continue
                else:
                    print 'ERROR'
                    exit()
            fl.write(opt['result']+'\n')
        fl.close()
