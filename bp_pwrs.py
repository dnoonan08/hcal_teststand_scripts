import sys
from hcal_teststand import ngfec
from hcal_teststand.hcal_teststand import teststand

ts = teststand("904at")		# Create teststand object for ngfec.send_commands()

cr = sys.argv[1]

commands = ['put HF{0}-bkp_pwr_enable 0'.format(cr), 'put HF{0}-bkp_pwr_enable 1'.format(cr), 'put HF{0}-bkp_reset 0'.format(cr), 'put HF{0}-bkp_reset 1'.format(cr), 'put HF{0}-bkp_reset 0'.format(cr)]
results = ngfec.send_commands(ts, cmds = commands, script = False)
for result in results:
	print result['cmd'][4:] + ': [' + result['result'] + ']'
