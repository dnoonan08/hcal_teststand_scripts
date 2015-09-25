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
	v = at.verbose
#	n_reads = at.n
	
	print uhtr.get_triggered_data(ts=ts, crate=at.be_crate, slot=at.be_slot, i_link=18, f="at_ici", script=True)
	raw = open("at_ici.txt", "r").read()
	data = uhtr.parse_l1a(raw=raw)
	for i_bx, ds in enumerate(data):
		print ds[0]
# /FUNCTIONS

# MAIN:
if __name__ == "__main__":
	main()
# /MAIN
