from hcal_teststand import ngfec
from hcal_teststand.hcal_teststand import teststand

ts = teststand("904at")		# Create teststand object for ngfec.send_commands()

print 'Enter the crate number to be reset:'
cr = int(raw_input())

commands = ['put HF{0}-bkp_pwr_enable 0'.format(cr), 'put HF{0}-bkp_pwr_enable 1'.format(cr), 'put HF{0}-bkp_reset 0'.format(cr), 'put HF{0}-bkp_reset 1'.format(cr), 'put HF{0}-bkp_reset 0'.format(cr)]

ngfec.send_commands(ts, cmds = commands, script = False)
