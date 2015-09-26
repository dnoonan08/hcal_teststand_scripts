####################################################################
# Type: SCRIPT (acceptance test)                                   #
#                                                                  #
# Description: ICI                                                 #
####################################################################

from hcal_teststand import *
from hcal_teststand.hcal_teststand import teststand
from hcal_teststand.utilities import *
import sys
import os
from optparse import OptionParser
from ROOT import *

# CLASSES:
# /CLASSES

# FUNCTIONS:
def main():
	# Make an acceptance test object:
	at = tests.acceptance(name="ici")		# Create an acceptance test.
	at.start(False)		# Start the acceptance test by printing some basic things.
	
	# Variables and simple set up:
	ts = at.ts
	qid = at.qid
	links = at.links
#	print links
	v = at.verbose
#	n_reads = at.n
	
	# Set up:
	ci_result = ts.set_ci(enable=True, script=False)		# Turn on internal charge-injection mode.
	if ci_result:
		for link in at.links:
			print link.n, link.qies
#			uhtr_out = uhtr.get_triggered_data(ts=ts, crate=at.be_crate, slot=at.be_slot, i_link=18, f="at_ici", script=True)
#			if uhtr_out:
#				raw = open("at_ici.txt", "r").read()
#				events = uhtr.parse_l1a(raw=raw)
#			#	print data
#				for event in events:
#					print "-----"
#					for i_bx, ds in enumerate(event):
#						print ds[1]
#			else:
#				print "ERROR (at_ici.main): Failed to get triggered data. If this is error is due to a timeout, you might need to turn the trigger on."
#				at.exit()
	else:
		print "ERROR (at_ici.main): Failed to set IC mode."
		at.exit()
# /FUNCTIONS

# MAIN:
if __name__ == "__main__":
	main()
# /MAIN
