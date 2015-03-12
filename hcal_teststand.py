from re import search
from subprocess import Popen, PIPE

# This dictionary stores the map between crate number and crate port:
crate_ports = {
	1: 4242,
}

def uhtr_commands(ip, cmds):
	log = ""
	raw_output = ""
	if isinstance(cmds, str):
		print "WARNING: You probably didn't intend to run the uHTRTool with only one command: {0}".format(cmds)
		print 'INFO: The "uhtr_commands" function takes a list of commands as an argument.'
		cmds = [cmds]
	cmds_str = ""
	for c in cmds:
		cmds_str += "{0}\n".format(c)
	raw_output = Popen(['printf "{0}" | uHTRtool.exe {1}'.format(cmds_str, ip)], shell = True, stdout = PIPE, stderr = PIPE).communicate()		# This puts the output of the command into a list called "raw_output_temp" the first element of the list is stdout, the second is stderr.
	log += "----------------------------\nYou ran the following script with the uHTRTool:\n\n{0}\n----------------------------".format(cmds_str)
#	print "========+========"
#	print raw_output[0] + raw_output[1]
#	print "========+========"
	return {
		"output": raw_output[0] + raw_output[1],
		"log": log,
	}

def ngccm_commands(crate_port, cmds):		# This executes ngccm commands in the slowest way, in order to read all of the output.
	raw_output = ""
	if isinstance(cmds, str):
		cmds = [cmds]
	for c in cmds:
		raw_output_temp = Popen(['printf "{0}" | ngccm -z -c -p {1}'.format(c + "\nquit", crate_port)], shell = True, stdout = PIPE, stderr = PIPE).communicate()		# This puts the output of the command into a list called "raw_output_temp" the first element of the list is stdout, the second is stderr.
		raw_output += raw_output_temp[0] + raw_output_temp[1]
	return raw_output

def ngccm_commands_fast(crate_port, cmds):		# This executes ngccm commands in a fast way, but some "get" results might not appear in the output.
	raw_output = ""
	if isinstance(cmds, str):
		cmds = [cmds]
	cmd = ""
	for c in cmds:
		cmd += "{0}\n".format(c)
	cmd += "quit\n"
	raw_output_temp = Popen(['printf "{0}" | ngccm -z -c -p {1}'.format(cmd, crate_port)], shell = True, stdout = PIPE, stderr = PIPE).communicate()		# This puts the output of the command into a list called "raw_output_temp" the first element of the list is stdout, the second is stderr.
	raw_output += raw_output_temp[0] + raw_output_temp[1]
	return raw_output

def read_temp(crate):
	log =""
	command = "get HF{0}-adc56_f".format(crate)
	raw_output = ngccm_commands(crate_ports[crate], command)
	temp = -1
	try:
		match = search("HF{0}-adc56_f:ReadResultF.*data=([\d\.])+".format(crate), raw_output)
		print match.group(0)
		print match.group(1)
		temp = float(match.group(1))
	except Exception as ex:
#		print raw_output
		log += 'Trying to find the temperature of Crate {0} with "{1}" resulted in: {2}\n'.format(crate, command, ex)
		match = search("\n(.*ERROR!!.*)\n", raw_output)
		if match:
			log+='The data string was "{0}".'.format(match.group(0).strip())
	return {
		"temp":	temp,
		"log":			log,
	}

if __name__ == "__main__":
	print "Hang on."
	print 'What you just ran is "hcal_teststand.py". This is a module, not a script. See the documentation (readme.md) for more information.'
