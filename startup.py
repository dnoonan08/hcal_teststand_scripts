from hcal_teststand import *
from hcal_teststand.hcal_teststand import *
from threading import Timer

from optparse import OptionParser
from checkLinks import *

ts = teststand("904at")
latestIglooVersion = '4.13'
latestBridgeVersion = '1.f'

from resetQIEdefaults import setQIEDefaults



parser = OptionParser()
parser.add_option("-t", "--teststand", dest="ts",
                  default="904at",
                  help="The name of the teststand you want to use (default is \"904at\")",
                  metavar="STR"
                  )
parser.add_option("-c", "--fecrate", dest="c",
                  default=-1,
                  help="FE crate (default is -1)",
                  metavar="INT"
                  )
parser.add_option("-s", "--feslot", dest="s",
                  default=-1,
                  help="FE slot (default is -1)",
                  metavar="INT"
                  )

(options, args) = parser.parse_args()
ts_name = options.ts
fe_crate = options.c
fe_slot = options.s

if fe_crate == -1:
    print 'specify a crate number'
    sys.exit()

ts = teststand(ts_name)
if fe_slot == -1:
    cmd = 'get HF{0}-[2,3,4,5,6,7,9,10,11,12,13,14]-bkp_temp_f'.format(fe_crate)
    output = ngfec.send_commands(ts, cmds = cmd, script = False, progbar = False)[0]
    slotList = [2,3,4,5,6,7,9,10,11,12,13,14]
    filledSlots = []
    temps = output['result'].split()
    for i in range(len(temps)):
        if float(temps[i])>0:
            filledSlots.append(slotList[i])
else:
    filledSlots = [int(fe_slot)]


print 'Running over slots', filledSlots


sleep(3)

cmds = ['put HF{0}-bkp_reset 0'.format(fe_crate),
        'put HF{0}-bkp_reset 1'.format(fe_crate),
        'put HF{0}-bkp_reset 0'.format(fe_crate),
        ]

output = ngfec.send_commands(ts, cmds = cmds, script=True, progbar = False)


for slot in filledSlots:
    print '-'*20
    setQIEDefaults(ts, fe_crate,slot)
    output = ngfec.send_commands(ts, cmds = 'get HF{0}-{1}-UniqueID'.format(fe_crate, slot), script = False, progbar = False)[0]['result']
    uID = "%s %s"%(output.split()[1],output.split()[2])
    print "Slot %i \n\tUniqueID %s"%(slot,uID)

    cmds = ['get HF{0}-{1}-iTop_FPGA_MAJOR_VERSION'.format(fe_crate,slot),
            'get HF{0}-{1}-iTop_FPGA_MINOR_VERSION'.format(fe_crate,slot),
            'get HF{0}-{1}-iBot_FPGA_MAJOR_VERSION'.format(fe_crate,slot),
            'get HF{0}-{1}-iBot_FPGA_MINOR_VERSION'.format(fe_crate,slot),
            'get HF{0}-{1}-B_FIRMVERSION_MAJOR'.format(fe_crate,slot),
            'get HF{0}-{1}-B_FIRMVERSION_MINOR'.format(fe_crate,slot),
            ]
    
    output = ngfec.send_commands(ts, cmds = cmds, script=True, progbar = False)

    iTopFW = '%s.%s' % (output[0]['result'].replace('0x',''),output[1]['result'].replace('0x',''))
    iBotFW = '%s.%s' % (output[2]['result'].replace('0x',''),output[3]['result'].replace('0x',''))
    BridgeFW = '%s.%s' % (output[4]['result'].replace('0x',''),output[5]['result'].replace('0x',''))

    if not iTopFW==latestIglooVersion: iTopFW += ' <===== Needs to be updates'
    if not iBotFW==latestIglooVersion: iBotFW += ' <===== Needs to be updates'
    if not BridgeFW==latestBridgeVersion: BridgeFW += ' <===== Needs to be updates'
    
    print '\t iTop Firmware %s'%iTopFW
    print '\t iBot Firmware %s'%iBotFW
    print '\t Bridge Firmware %s'%BridgeFW

        
cmds = ['put HF{0}-bkp_reset 0'.format(fe_crate),
        'put HF{0}-bkp_reset 1'.format(fe_crate),
        'put HF{0}-bkp_reset 0'.format(fe_crate),
        ]

output = ngfec.send_commands(ts, cmds = cmds, script=True, progbar = False)
