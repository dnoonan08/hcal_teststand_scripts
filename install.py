####################################################################
# Type: SCRIPT                                                     #
#                                                                  #
# Description: This script installs the repository. It creates     #
# configuration files and set up scripts.                          #
#                                                                  #
# Notes: Keep this script compatible with Python 2.4. That means   #
# don't use format!                                                #
####################################################################

from re import search, split
from hcal_teststand import install
#from hcal_teststand import amc13		# Not compatible...

# FUNCTIONS:
# /FUNCTIONS

# MAIN:
if __name__ == "__main__":
	install.make_amc13_configs()
	install.make_setup_scripts("teststands.txt")
 # /MAIN
