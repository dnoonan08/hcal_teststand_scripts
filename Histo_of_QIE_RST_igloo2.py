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
	print "\nATTENTION: This script runs on the QIE card in slot {0} of crate {1}. If you want to change this, edit lines 30-31.".format(i_slot, i_crate)
	
	for side in ["Top", "Bot"]:
		print "======================= {0} ======================================".format(side)
		# Define ngccm scripts:
		scripts = [
			[
				"get HF{0}-{1}-i{2}_FPGA_MAJOR_VERSION".format(i_crate, i_slot, side),
				"get HF{0}-{1}-i{2}_FPGA_MINOR_VERSION".format(i_crate, i_slot, side),
				"get fec1-qie_reset_cnt",
				"get HF{0}-{1}-i{2}_RST_QIE_count".format(i_crate, i_slot, side),
			],
			[
				"get fec1-qie_reset_cnt",
				"get HF{0}-{1}-i{2}_RST_QIE_count".format(i_crate, i_slot, side),
			],
			[
				"get fec1-qie_reset_cnt",
				"get HF{0}-{1}-i{2}_RST_QIE_count".format(i_crate, i_slot, side),
				"get HF{0}-{1}-i{2}_CntrReg".format(i_crate, i_slot, side),
				"put HF{0}-{1}-i{2}_CntrReg 0x20".format(i_crate, i_slot, side),
			],
			[
				"get HF{0}-{1}-i{2}_CntrReg".format(i_crate, i_slot, side),
				"put HF{0}-{1}-i{2}_CntrReg 0x0".format(i_crate, i_slot, side),
			],
			[
				"get HF{0}-{1}-i{2}_Spy96bits".format(i_crate, i_slot, side),
				"put HF{0}-{1}-i{2}_CntrReg 0x10".format(i_crate, i_slot, side),
			],
			[
				"put HF{0}-{1}-i{2}_CntrReg 0x0".format(i_crate, i_slot, side),
				"get HF{0}-{1}-i{2}_Spy96bits".format(i_crate, i_slot, side),
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
