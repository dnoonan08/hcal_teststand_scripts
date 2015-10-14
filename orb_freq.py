import time
from hcal_teststand import ngfec
from hcal_teststand.hcal_teststand import teststand
ts = teststand("904at")

commands = ['get HF1-2-iTop_RST_QIE_count', 'get HF1-2-iBot_RST_QIE_count', 'get HF1-2-B_RESQIECOUNTER', 'get HF1-5-iTop_RST_QIE_count', 'get HF1-5-iBot_RST_QIE_count', 'get HF1-5-B_RESQIECOUNTER', 'get HF2-2-iTop_RST_QIE_count', 'get HF2-2-iBot_RST_QIE_count', 'get HF2-2-B_RESQIECOUNTER', 'get fec1-qie_reset_cnt']

outputi = ngfec.send_commands(ts, cmds = commands, script = False)
time.sleep(10)
outputf = ngfec.send_commands(ts, cmds = commands, script = False)
print 'Orbit frequencies from various components:'
for i, j in zip(outputi, outputf):
	print '\t{0}: \t{1:.3f} kHz'.format(i['cmd'], (int(j['result'], 16)-int(i['result'], 16))/((j['times'][0]-i['times'][0])*1000.))
