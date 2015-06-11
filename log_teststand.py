####################################################################
# Type: SCRIPT                                                     #
#                                                                  #
# Description: This script logs all BRIDGE, IGLOO2, and nGCCM      #
# registers as well as the power supply and time. This script is   #
# to run continuously, logging at a user set period.               #
####################################################################

from hcal_teststand import *
from hcal_teststand.hcal_teststand import teststand
from hcal_teststand.utilities import *
import sys
import os
from optparse import OptionParser
from time import sleep, time

# CLASSES:
# /CLASSES

# FUNCTIONS:
def log_temp(ts):
	log = ""
	temps = hcal_teststand.get_temps(ts)[1]		# Only care about crate 1
	log += "[!!]%% TEMPERATURES\n[2 sensors] (There are two temperature sensors on the ngCCM. One is near the fan inlet, which is the bottom of the ngCCM. The other is near the 3.3V DC/DC module. The idea is that the bottom one should give you a reading of the ambient temperature, especially if the fans are on. Then you can compute what the temperature rise across the board is.)\n"
	for result in temps:
		log += "{0} -> {1}\n".format(result["cmd"], result["result"])
	return log

def log_power(ts):
	log = ""
	t0 = time_string()		# Get the time before. I get the time again after everything.
	power_fe = ts_157.get_power(ts)
	log += "%% POWER\n{0:.2f} V\n{1:.2f} A\n".format(power_fe["V"], power_fe["I"])
	power_ngccm = ngccm.get_power(ts)[1]		# Take only the crate 1 results (there's only one crate, anyway).
	for result in power_ngccm:
		log += "{0} -> {1}\n".format(result["cmd"], result["result"])
	return log

def log_registers(ts=False, scale=0):		# Scale 0 is the slim set of registers, 1 is full.
	log = ""
	log += "[!!]%% REGISTERS\n"
	if scale == 0:
		cmds = [
			"get fec1-LHC_clk_freq",
			"get HF1-mezz_ONES",		# Check that this is all 1s.
			"get HF1-mezz_ZEROES",		# Check that is is all 0s.
		]
	elif scale == 1:
		cmds = ngccm.cmds_HF1_2
	else:
		cmds = []
	output = ngccm.send_commands_parsed(ts.ngccm_port, cmds)["output"]
	for result in output:
		log += "{0} -> {1}\n".format(result["cmd"], result["result"])
	return log

def log_links(ts, scale=0):
	log = ""
	active_links = uhtr.find_links(ts.uhtr_ips[0])
	log += "[!!]%% LINKS\n{0}\n".format(active_links)
	if scale == 1:
		log += "[data] (There are two temperature sensors on the ngCCM. One is near the fan inlet, which is the bottom of the ngCCM. The other is near the 3.3V DC/DC module. The idea is that the bottom one should give you a reading of the ambient temperature, especially if the fans are on. Then you can compute what the temperature rise across the board is.)\n"
	return log

def record(ts=False, path="data/unsorted", scale=0):
	log = ""
	t_string = time_string()[:-4]
	t0 = time_string()

	# Log basics:
	log += log_power(ts)		# Power
	log += "\n"
	log += log_temp(ts)		# Temperature
	log += "\n"
	
	# Log registers:
	log += log_registers(ts=ts, scale=scale)
	log += "\n"
	
	# Log links:
	log += log_links(ts, scale=scale)
	log += "\n"
	
	# Log other:
	log += "[!!]%% WHAT?\n(There is an error counter, which I believe is in the I2C register. This only counts GBT errors from GLIB to ngCCM. I doubt that Ozgur has updated the GLIB v3 to also count errors from ngCCM to GLIB. That would be useful to have if the counter exists.\nI also want to add, if there is time, an error counter of TMR errors. For the DFN macro TMR code, I implement an error output that goes high if all three outputs are not the same value. This would monitor only a couple of D F/Fs but I think it would be useful to see if any TMR errors are detected.)\n\n"

	# Time:
	t1 = time_string()
	log = "%% TIME\n{0}\n{1}\n\n".format(t0, t1) + log

	# Write log:
	path += "/{0}".format(t_string[:-7])
	print ">> {0}: Created log file named \"{1}.log\" in directory \"{2}\"".format(t1[:-4], t_string, path)
	if not os.path.exists(path):
		os.makedirs(path)
	with open("{0}/{1}.log".format(path, t_string), "w") as out:
		out.write(log.strip())
	return log
# /FUNCTIONS

# MAIN:
if __name__ == "__main__":
	# Script arguments:
	directory = "data/logs_157"
	parser = OptionParser()
	parser.add_option("-t", "--teststand", dest="ts",
		default="157",
		help="The name of the teststand you want to use (default is \"157\"). Unless you specify the path, the directory will be put in \"data\".",
		metavar="STR"
	)
	parser.add_option("-o", "--fileName", dest="out",
		default="",
		help="The name of the directory you want to output the logs to (default is \"ts_157\").".format(directory),
		metavar="STR"
	)
	parser.add_option("-T", "--period", dest="T",
		default=1,
		help="The logging period in minutes (default is 1).",
		metavar="FLOAT"
	)
	(options, args) = parser.parse_args()
	name = options.ts
	period = float(options.T)
	if not options.out:
		path = "data/ts_{0}".format(name)
	elif "/" in options.out:
		path = options.out
	else:
		path = "data/" + options.out
	
	# Set up teststand:
	ts = teststand(name)
	
	# Print information:
	print ">> The output directory is {0}.".format(path)
	print ">> The logging period is {0} minutes.".format(period)
	print ">> (A full log will be taken every hour.)"
	
	# Logging loop:
	z = True
	t0 = 0
	t0_long = time()
	while z == True:
		dt = time() - t0
		dt_long = time() - t0_long
		if (dt_long > 3600):
			t0_long = time()
			record(ts=ts, path=path, scale=1)
		if (dt > period*60):
			t0 = time()
			record(ts=ts, path=path, scale=0)
		else:
			sleep(1)
#		z = False
	
# /MAIN
