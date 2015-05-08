####################################################################
# Type: SCRIPT                                                     #
#                                                                  #
# Description: [Put a description here.]                           #
####################################################################

from hcal_teststand import *
from hcal_teststand.hcal_teststand import *
import sys

# CLASSES:
# /CLASSES

# FUNCTIONS:
# /FUNCTIONS

# MAIN:
if __name__ == "__main__":
	# Arguments:
	name = ""
	if len(sys.argv) == 1:
		name = "904"
	elif len(sys.argv) == 2:
		name = sys.argv[1]
	else:
		name = "904"
	ts = teststand(name)		# Initialize a teststand object. This object stores the teststand configuration and has a number of useful methods.
	
	# Variables:
	i_crate = 1
	i_slot = 2
	
	# Define ngccm scripts:
	scripts = [
		[
			"get HF{0}-{1}-iTop_FPGA_MAJOR_VERSION".format(i_crate, i_slot),
			"get HF{0}-{1}-iTop_FPGA_MINOR_VERSION".format(i_crate, i_slot),
			"get fec1-qie_reset_cnt",
			"get HF{0}-{1}-iTop_RST_QIE_count".format(i_crate, i_slot),
		],
		[
			"get fec1-qie_reset_cnt",
			"get HF{0}-{1}-iTop_RST_QIE_count".format(i_crate, i_slot),
		],
		[
			"get fec1-qie_reset_cnt",
			"get HF{0}-{1}-iTop_RST_QIE_count".format(i_crate, i_slot),
			"get HF{0}-{1}-iTop_CntrReg".format(i_crate, i_slot),
			"put HF{0}-{1}-iTop_CntrReg 0x20".format(i_crate, i_slot),
		],
		[
			"get HF{0}-{1}-iTop_CntrReg".format(i_crate, i_slot),
			"put HF{0}-{1}-iTop_CntrReg 0x0".format(i_crate, i_slot),
		],
		[
			"get HF{0}-{1}-iTop_Spy96bits".format(i_crate, i_slot),
			"put HF{0}-{1}-iTop_CntrReg 0x10".format(i_crate, i_slot),
		],
		[
			"put HF{0}-{1}-iTop_CntrReg 0x0".format(i_crate, i_slot),
			"get HF{0}-{1}-iTop_Spy96bits".format(i_crate, i_slot),
		]
	]
	
	# Run ngccm scripts:
	for script in scripts:
		print ">> Running script number {0}".format(scripts.index(script))
		output = ngccm.send_commands_parsed(ts.ngccm_port, script)["output"]
		for cmd in output:
			print "<< {0} -> {1}".format(cmd["cmd"], cmd["result"])
		print ""
# /MAIN
