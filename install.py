from hcal_teststand import *

def make_amc13_configs(f):
	names = []
	ts_info = parse_ts_configuration(f)
	for name, info in ts_info.iteritems():
		if info:
			string = '''
<?xml version="1.0" encoding="UTF-8"?>
<connections>
	<connection id="T1" uri="chtcp-2.0://localhost:10203?target={0}:50001" address_table="file:///opt/cactus/etc/amc13/AMC13XG_T1_v{1}.xml" />
	<connection id="T2" uri="chtcp-2.0://localhost:10203?target={2}:50001" address_table="file:///opt/cactus/etc/amc13/AMC13XG_T2_v{3}.xml" />
</connections>
			'''.format(info["amc13_ips"][0], info["amc13_versions"][0], info["amc13_ips"][1], info["amc13_versions"][1]).strip()
			try:
				out = open("configuration/amc13_{0}_config.xml".format(name), "w")
				out.write(string)
				names.append(name)
			except Exception as ex:
				print ex
		else:
			print "ERROR: Didn't make an AMC13 configuration file for {0}.".format(name)
	return names

def make_setup_scripts(f):
	names = []
	ts_info = parse_ts_configuration(f)
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
			try:
				out = open("configuration/setup_{0}.sh".format(name), "w")
				out.write(string)
				names.append(name)
			except Exception as ex:
				print ex
		else:
			print "ERROR: Didn't make an setup script for {0}.".format(name)
	return names

if __name__ == "__main__":
	make_amc13_configs("teststands.txt")
	make_setup_scripts("teststands.txt")

