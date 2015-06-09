import pexpect
from utilities import time_string
from time import time

def get_power(ts):
	p = pexpect.spawn('/home/daq/gpib/kam/lowVoltage')		# Run script.
	p.expect(pexpect.EOF)		# Wait for the script to finish.
	raw_output = p.before.strip()		# Collect all of the script's output.
	results = [float(value[:-1]) for value in raw_output.split()]
	return {
		"v": results[0],
		"a": results[1],
#		"time": time_string(),
		"time": time(),
	}
