####################################################################
# Type: SCRIPT                                                     #
#                                                                  #
# Description: This is a script skeleton.                          #
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
	name = ""
	if len(sys.argv) == 1:
		name = "904"
	elif len(sys.argv) == 2:
		name = sys.argv[1]
	else:
		name = "904"
	ts = teststand(name)		# Initialize a teststand object. This object stores the teststand configuration and has a number of useful methods.
	print "\nYou've just run a script that's a skeleton for making your own script."
	# Print out some information about the teststand:
	print ">> The teststand you're using is named {0}.".format(ts.name)
	print ">> The crate and QIE card organization for the teststand is below:\n{0}".format(ts.fe)
# /MAIN
