# This module contains functions for talking to the MCH.

from re import search
from subprocess import Popen, PIPE

# FUNCTIONS:
def get_status(ts):
	status = {}
	status["status"] = []
	# Ping MCH:
	ping_result = Popen(["ping -c 1 {0}".format(ts.mch_ip)], shell = True, stdout = PIPE, stderr = PIPE).stdout.read()
	if ping_result:
		status["status"].append(1)
	else:
		status["status"].append(0)
	return status
