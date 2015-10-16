import time
from hcal_teststand import ngfec
from hcal_teststand.hcal_teststand import teststand
ts = teststand("904at")

commands = []
crsl = {2: [2, 3, 4, 5, 6]}	# crate/slot dict. keys: crates, values: slots
for crate, slots in crsl.iteritems():
	for slot in slots:
		commands.extend(['get HF{0}-{1}-iTop_RST_QIE_count'.format(crate, slot), 'get HF{0}-{1}-iBot_RST_QIE_count'.format(crate, slot), 'get HF{0}-{1}-B_RESQIECOUNTER'.format(crate, slot), 'get fec1-qie_reset_cnt'])

outputi = ngfec.send_commands(ts, cmds = commands, script = False)
time.sleep(10)
outputf = ngfec.send_commands(ts, cmds = commands, script = False)
print 'Orbit frequencies from various components:'
for i, j in zip(outputi, outputf):
	print '\t{0}: \t{1:.3f} kHz'.format(i['cmd'], (int(j['result'], 16)-int(i['result'], 16))/((j['times'][0]-i['times'][0])*1000.))
