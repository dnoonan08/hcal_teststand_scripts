from re import search
from subprocess import Popen, PIPE

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

def ngccm_commands(crate_port, cmd):
	raw_output = ""
	if isinstance(cmd, str):
		raw_output_temp = Popen(['printf "{0}" | ngccm -z -c -p {1}'.format(cmd + "\nquit", crate_port)], shell = True, stdout = PIPE, stderr = PIPE).communicate()		# This puts the output of the command into a list called "raw_output_temp" the first element of the list is stdout, the second is stderr.
		raw_output += raw_output_temp[0] #+ raw_output_temp[1]
	elif isinstance(cmd, list):
		for c in cmd:
			raw_output_temp = Popen(['printf "{0}" | ngccm -z -c -p {1}'.format(c + "\nquit", crate_port)], shell = True, stdout = PIPE, stderr = PIPE).communicate()		# This puts the output of the command into a list called "raw_output_temp" the first element of the list is stdout, the second is stderr.
			raw_output += raw_output_temp[0] + raw_output_temp[1]
	return raw_output

if __name__ == "__main__":
	print "Hang on."
	print 'What you just ran is "hcal_teststand.py". This is a module, not a script. See the documentation (readme.md) for more information.'
