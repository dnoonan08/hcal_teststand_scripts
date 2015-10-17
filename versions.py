####################################################################
# Type: SCRIPT                                                     #
#                                                                  #
# Description: This script prints out version information for all  #
# of the components in a teststand.                                #
####################################################################

from optparse import OptionParser
from hcal_teststand import *
from hcal_teststand.hcal_teststand import *
import sys


# FUNCTIONS:
def main():
	# Arguments and variables:
	parser = OptionParser()
	parser.add_option("-t", "--teststand", dest="ts",
		default="904",
		help="The name of the teststand you want to use (default is \"904at\")",
		metavar="STR"
	)
	(options, args) = parser.parse_args()
	name = options.ts
	ts = teststand(name)
	
	# Get information:
	print "\nFinding the versions of the {0} teststand...".format(name)
	result = ts.update()
	if result:
		# Print information:
		print_versions(ts)
	else:
		print "\tERROR (versions): Couldn't update the teststand object."
		print "\t[!!] Script aborted."
#	print_amc13_info(ts)
#	print_glib_info(ts)
#	print_uhtr_info(ts)
#	print_ngccm_info(ts)
#	print_qie_info(ts)
##	print_bridge_info(ts, 1, 2)
##	print_igloo_info(ts, 1, 1)

def print_versions(ts=None):
	# AMC13s:
	print "* AMC13s:"
	for crate, amc13 in ts.amc13s.iteritems():
		print "\t[OK] BE Crate {0}: FW = {1}, SW = {2}".format(crate, amc13.fw, amc13.sw)
	
	# FC7s:
	print "* FC7s:"
	for n, fc7 in ts.fc7s.iteritems():
		print "\t[OK] FEC{0}: FW = {1} {2}".format(n, ".".join(["{0:02d}".format(i) for i in fc7.fw[0]]), fc7.fw[1])
	
	# ngCCMs:
	print "* ngCCMs:"
	for crate, ngccm in ts.ngccms.iteritems():
		if isinstance(ngccm.id, list):
			ngccm_id = " ".join(ngccm.id)
		else:
			ngccm_id = "?"
		print "\t[OK] FE Crate {0}: FW = {1}, ID = {2}".format(crate, ngccm.fw, ngccm_id)
	
	# uHTRs:
	print "* uHTRs:"
	for crate_slot, uhtr in ts.uhtrs.iteritems():
		print "\t[OK] BE Crate {0}, Slot {1}: FW = {2}".format(crate_slot[0], crate_slot[1], uhtr.fws)
	
	# QIEs:
	print "* QIEs:"
	for crate_slot, qie in ts.qies.iteritems():
		print "\t[OK] FE Crate {0}, Slot {1}: FW = {2}, ID = {3}".format(crate_slot[0], crate_slot[1], qie.fws, qie.id)

def print_amc13_info(ts):		# Fetches and prints AMC13 version information.
	amc_info = amc13.get_info(ts=ts)
	print "* AMC13  ================================="
	if (amc_info["sn"] == -1):
		print "\tERROR: There was a problem fetching the AMC13 information."
		print "\tThe log is below:\n++++++++++++++ LOG ++++++++++++++++++\n{0}\n+++++++++++++ /LOG ++++++++++++++++++".format(amc_info["log"])
	else:
		print "\tSN: {0}".format(amc_info["sn"])
		print "\tFW version (T1): {0:04d}".format(amc_info["version_fw"][0])
		print "\tFW version (T2): {0:04d}".format(amc_info["version_fw"][1])
		print "\tSW version: {0}".format(amc_info["version_sw"])
		print "\tNotes: \"Tx\" stands for \"Tongue x\", different boards in the AMC13. Only T1 and T2 talk to the BE backplane."
#		print "\tLog: {0}".format(amc_info["log"])

def print_glib_info(ts):
	glib_info = glib.get_info(ts)
	print "* GLIB   ================================="
	if (glib_info["version_fw"] == "000000"):
		print "\tERROR: There was a problem fetching the GLIB information."
		print "\tThe log is below:\n++++++++++++++ LOG ++++++++++++++++++\n{0}\n+++++++++++++ /LOG ++++++++++++++++++".format(glib_info["log"])
	else:
		print "\tFW version: {0}".format(glib_info["version_fw"])

def print_uhtr_info(ts):
	uhtr_infos = uhtr.get_info(ts)
	for uhtr_info in uhtr_infos:
		print "* uHTR (Slot {0:02d}) =========================".format(uhtr_info["slot"])
		print "\tFW version (front): {0}".format(uhtr_info["version_fw_front_str"])
		print "\tFW type (front): {0} ({1})".format(uhtr_info["version_fw_type_front"][0], uhtr_info["version_fw_type_front"][1])
		print "\tFW version (back): {0}".format(uhtr_info["version_fw_back_str"])
		print "\tFW type (back): {0} ({1})".format(uhtr_info["version_fw_type_back"][0], uhtr_info["version_fw_type_back"][1])
		print "\tSW version: ? (it's not currently possible to find out)"

def print_ngccm_info(ts):
	ngccm_info = ngccm.get_info(ts, ts.fe_crates[0])
	print "* ngCCM  ================================="
	if (ngccm_info["version_fw_mez_major"] == -1):
		print "\tERROR: There was a problem fetching the ngCCM information."
		print "\tThe log is below:\n++++++++++++++ LOG ++++++++++++++++++\n{0}\n+++++++++++++ /LOG ++++++++++++++++++".format(ngccm_info["log"])
	else:
		print "\tFW version (mezzanine): {0}".format(ngccm_info["version_fw_mez"])
		print "\tSW version: {0}".format(ngccm_info["version_sw"])

def print_bridge_info(ts, crate, slot):
	bridge_info = qie.get_bridge_info(ts, crate, slot)
	print "* BRIDGE (Crate {0}, Slot {1}) ===============".format(crate, slot)
	if (bridge_info["version_fw"] == "00.00.0000"):
		print "\tERROR: There was a problem fetching the BRIDGE information."
		print "\tThe log is below:\n++++++++++++++ LOG ++++++++++++++++++\n{0}\n+++++++++++++ /LOG ++++++++++++++++++".format(bridge_info["log"])
	else:
		print "\tFW version: {0}".format(bridge_info["version_fw"])

def print_igloo_info(ts, crate, slot):
	igloo_info = qie.get_igloo_info(ts, crate, slot)
	print "* IGLOO  (Crate {0}, Slot {1}) ===============".format(crate, slot)
	if (igloo_info["version_fw_top"] == "00.00"):
		print "\tERROR: There was a problem fetching the IGLOO's top FPGA information."
		print "\tThe log is below:\n++++++++++++++ LOG ++++++++++++++++++\n{0}\n+++++++++++++ /LOG ++++++++++++++++++".format(igloo_info["log"])
	else:
		print "\tFW version (top): {0}".format(igloo_info["version_fw_top"])
	if (igloo_info["version_fw_bot"] == "00.00"):
		print "\tERROR: There was a problem fetching the IGLOO's bottom FPGA information."
		print "\tThe log is below:\n++++++++++++++ LOG ++++++++++++++++++\n{0}\n+++++++++++++ /LOG ++++++++++++++++++".format(igloo_info["log"])
	else:
		print "\tFW version (bottom): {0}".format(igloo_info["version_fw_bot"])

def print_qie_info_1(ts, crate, slot):
	qie_info = qie.get_info(ts, crate, slot)
	igloo_info = qie_info["igloo"]
	bridge_info = qie_info["bridge"]
	print "* QIE card (crate {0}, slot {1:02d}) =================".format(crate, slot)
	if (igloo_info["version_fw_top"] == "00.00"):
		print "\tERROR: There was a problem fetching the IGLOO's top FPGA information."
#		print "\tThe log is below:\n++++++++++++++ LOG ++++++++++++++++++\n{0}\n+++++++++++++ /LOG ++++++++++++++++++".format(igloo_info["log"])
	else:
		print "\tIGLOO2 FW version (top): {0}".format(igloo_info["version_fw_top"])
	if (igloo_info["version_fw_bot"] == "00.00"):
		print "\tERROR: There was a problem fetching the IGLOO's bottom FPGA information."
#		print "\tThe log is below:\n++++++++++++++ LOG ++++++++++++++++++\n{0}\n+++++++++++++ /LOG ++++++++++++++++++".format(igloo_info["log"])
	else:
		print "\tIGLOO2 FW version (bottom): {0}".format(igloo_info["version_fw_bot"])
	if (bridge_info["version_fw"] == "00.00.0000"):
		print "\tERROR: There was a problem fetching the BRIDGE information."
#		print "\tThe log is below:\n++++++++++++++ LOG ++++++++++++++++++\n{0}\n+++++++++++++ /LOG ++++++++++++++++++".format(bridge_info["log"])
	else:
		print "\tBRIDGE FW version: {0}".format(bridge_info["version_fw"])

def print_qie_info(ts):
	for crate, slots in ts.fe.iteritems():
		for slot in slots:
			print_qie_info_1(ts, crate, slot)
# /FUNCTIONS

# MAIN:
if __name__ == "__main__":
	main()
# /MAIN
