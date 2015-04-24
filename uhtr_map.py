from hcal_teststand import *
import uhtr
import ngccm
import numpy
import sys
import qie

################################################
# container to hold QIE mapping for all
# of the links of a given uHTR
# ... eventually, I would like this to 
# read and write xml files so that a snap shot 
# of the cable mapping can be saved 
################################################	
class uHTRlinkMap : 
	
	links = []

	def __init__( self ):
		
		for i in range(96):
			self.links.append(uhtr.link())

# FUNCTIONS:
def read_links(ip) : # Looks at the spy dumps of all of the active channels and parses out the QIE card's unique ID and fiber information corresponding to the target qie channels
	active_links = uhtr.get_links(ip)
	uhtr_map = uHTRlinkMap()
	
	for link_ in uhtr_map.links: 
		if uhtr_map.links.index(link_) in active_links : 
			#print "link",uhtr_map.links.index(link_),"on..."
			link_.on = True
			uhtr_read = uhtr.get_data(ip, 3, uhtr_map.links.index(link_))		# grab spy dump and parse information about this link
#			print uhtr_read["output"]
			data = [""]*6
			for line in uhtr_read["output"].split("\n"):
				#print line
				if line.find("TOP fiber") != -1 : 
					#print line.split(" ")[5]
					data[0] = line.split(" ")[5][1:5]
					link_.qie_half=1
					link_.qie_fiber = int(line.split(" ")[9])
				if line.find("BOTTOM fiber") != -1 : 
					#print line.split(" ")[5]
					data[0] = line.split(" ")[5][1:5]
					link_.qie_half=0
					link_.qie_fiber = int(line.split(" ")[9])
				if line.find("CAPIDS") != -1 :
					data[1] = line.split(" ")[5][1:5]
				if line.find("ADCs") != -1 :
					data[2] = line.split(" ")[5][1:5]
				if line.find("LE-TDC") != -1 :
					data[3] = line.split(" ")[5][1:5]
				if line.find("TE-TDC") != -1 :
					data[4] = line.split(" ")[5][1:5]
				link_.qie_uniqueID = "0x{0}{1}{2}{3} 0x{4}{5}{6}{7}".format(
					data[2][0:2],
					data[2][2:4],
					data[1][0:2],
					data[1][2:4],
					data[4][0:2],
					data[4][2:4],
					data[3][0:2],
					data[3][2:4]
				)
			#link_.Print()
	
	return uhtr_map


def link_test_modeB(ts, crate, slot, yesNo): # if yesNo -> enable test mode B: puts qie card unique ID into data stream
	if yesNo:
		return ngccm.send_commands(ts.ngccm_port , ["put HF{0}-{1}-iTop_LinkTestMode 0x7".format(crate,slot),"put HF{0}-{1}-iBot_LinkTestMode 0x7".format(crate,slot)] ) 
	else :
		return ngccm.send_commands(ts.ngccm_port , ["put HF{0}-{1}-iTop_LinkTestMode 0x0".format(crate,slot),"put HF{0}-{1}-iBot_LinkTestMode 0x0".format(crate,slot)] )


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
	
	# For each QIE card, put its unique ID into the IGLOO registers and turn on link test mode:
	set_mode_all(ts, 2)		# 0: normal mode, 1: link test mode A (test mode string), 2: link test mode B (IGLOO register)
	for crate, slots in ts.fe.iteritems():
		for slot in slots:
#			link_test_modeB(ts, crate, slot, True)
			is_set = ngccm.set_unique_id(ts, crate, slot)		# Set the QIE card's unique ID into the correct IGLOO registers.
	
	# Figure out which uHTR link maps to which unique ID:
	for ip in ts.uhtr_ips:
		uhtr_map = read_links(ip)
		active_links = [link for link in uhtr_map.links if link.on]
		print "Below are the active links of the uHTR at {0}:".format(ip)
		for link in active_links:
			if link.on:
				print "==== Link {0} ====".format(uhtr_map.links.index(link))
				link.Print()
				print ""
	
	# Put the IGLOOs back into normal readout mode:
	set_mode_all(ts, 0)

