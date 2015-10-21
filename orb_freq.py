import time
from hcal_teststand import ngfec
from hcal_teststand.hcal_teststand import teststand

ts = teststand("904at")		# Create teststand object for ngfec.send_commands()
commands = []			# List of commands to be sent to ngFEC tool
crsl = {}			# Crate/Slot dict. keys: crates, values: slots

crates = [2, 3, 4, 5]		# Crates to be used
#crates = range(1, 7)		# ALL CRATES!!
FC7s = [1, 2]			# FC7s to be used

for crate in crates:
	crsl.update({crate: range(1, 15)})
for crate, slots in crsl.iteritems():
	for slot in slots:
		commands.extend(['get HF{0}-{1}-iTop_RST_QIE_count'.format(crate, slot), 'get HF{0}-{1}-iBot_RST_QIE_count'.format(crate, slot), 'get HF{0}-{1}-B_RESQIECOUNTER'.format(crate, slot)])
for FC7 in FC7s:
	commands.extend(['get fec{0}-qie_reset_cnt'.format(FC7)])

outputi = ngfec.send_commands(ts, cmds = commands, script = False)
time.sleep(10)
outputf = ngfec.send_commands(ts, cmds = commands, script = False)

print 'Orbit frequencies from various components:'
for i, j in zip(outputi, outputf):
	if not ('ERROR' in j['result'] or 'ERROR' in i['result']):
		print '\t{0}: \t{1:.3f} kHz'.format(i['cmd'], (int(j['result'], 16)-int(i['result'], 16))/((j['times'][0]-i['times'][0])*1000.))
