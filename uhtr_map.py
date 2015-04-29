from hcal_teststand import *
import uhtr
import ngccm
import numpy
import sys
import qie

# FUNCTIONS:
# /FUNCTIONS

# MAIN:
if __name__ == "__main__":
	name = ""
	out_file = ""
	if len(sys.argv) == 1:
		name = "904"
		out_file = "uhtr_map.xml"
	elif len(sys.argv) == 2:
		name = sys.argv[1]
		out_file = "uhtr_map.xml"
	elif len(sys.argv) == 3:
		name = sys.argv[1]
		out_file = sys.argv[2]
	else:
		name = "904"
		out_file = "uhtr_map.xml"
	ts = teststand(name)
#	print ts.fe
	
	log = ""
	
	print "The {0} teststand has {1} uHTR(s) at the following IP addresses:".format(ts.name, len(ts.uhtr_ips))
	for ip in ts.uhtr_ips:
		print "\t{0}".format(ip)
	print "\n"
	link_container = uhtr.get_links_all(ts)
	for ip, links in link_container.iteritems():
		print "Below are the active links of the uHTR at {0}:".format(ip)
		for link in links:
			if link.on:
				print "==== Link {0} ====".format(link.n)
				link.Print()
				print ""
# /MAIN
