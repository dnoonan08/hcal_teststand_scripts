####################################################################
# Type: SCRIPT                                                     #
#                                                                  #
# Description: This script installs the repository. It creates     #
# configuration files and set up scripts.                          #
#                                                                  #
# Notes: Keep this script compatible with Python 2.4.              #
####################################################################

from re import search, split
from hcal_teststand import hcal_teststand
from hcal_teststand import amc13

# FUNCTIONS:
def make_amc13_configs(f="teststands.txt"):		# Write configuration files for AMC13.
	names = []
	ts_info = hcal_teststand.parse_ts_configuration(f=f)
	for name, info in ts_info.iteritems():
		if "control_hub" in info:
			ch = info["control_hub"]
		else:
			ch = "localhost"
		if info:
			string = '<?xml version="1.0" encoding="UTF-8"?>\n<connections>\n'
			amc13s = [ips for ips in info["amc13_ips"] if ips]
			for i, ips in enumerate(amc13s):
				string += '\t<!-- AMC13 with SN = {0} -->\n'.format(amc13.sn_from_ip(ips[0]))
				string += '\t<connection id="{0}T1" uri="chtcp-2.0://'.format(str(i) + "." if len(amc13s) > 1 else "") + ch + ':10203?target=' + ips[0] + ':50001" address_table="file:///opt/cactus/etc/amc13/AMC13XG_T1.xml" />\n'
				string += '\t<connection id="{0}T2" uri="chtcp-2.0://'.format(str(i) + "." if len(amc13s) > 1 else "") + ch + ':10203?target=' + ips[1] + ':50001" address_table="file:///opt/cactus/etc/amc13/AMC13XG_T2.xml" />\n'
			string += '</connections>'
			try:
				out = open("configuration/amc13_" + name + "_config.xml", "w")
				out.write(string)
				names.append(name)
			except Exception, ex:		# This notation is compatible with older versions of Python. It's good to keep this compatible so that the script can be run from the B904 head node.
				print ex
		else:
			print "ERROR: Didn't make an AMC13 configuration file for " + name + "."
	return names

def make_setup_scripts(f):		# Write the set up scripts.
	names = []
	ts_info = hcal_teststand.parse_ts_configuration(f)
	for name, info in ts_info.iteritems():
		string = ""
		if info:
			if name == "bhm":
				string = '''
source /nfshome0/hcalsw/bin/env.sh
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/ngccm/lib
export PATH=$PATH:/opt/ngccm/bin
				'''.strip()
			elif name == "904":
				string = '''
source /nfshome0/hcalsw/bin/env.sh
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/nfshome0/hcalpro/ngFEC
export PATH=$PATH:/nfshome0/hcalpro/ngFEC
				'''.strip()
			elif name == "157":
				string = '''
source /home/daq/environment.sh
				'''.strip()
			elif name == "fnal":
				string = '''
source /home/hcalpro/tote/env.sh
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/hcalpro/ngFEC
export PATH=$PATH:/home/hcalpro/ngFEC
				'''.strip()
			try:
				out = open("configuration/setup_" + name + ".sh", "w")
				out.write(string)
				names.append(name)
			except Exception, ex:
				print ex
		else:
			print "ERROR: Didn't make an setup script for " + name + "."
	return names
# /FUNCTIONS

# MAIN:
if __name__ == "__main__":
	make_amc13_configs()
	make_setup_scripts("teststands.txt")
 # /MAIN
