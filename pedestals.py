from hcal_teststand import *
import uhtr
import ngccm
import numpy
import sys
import qie

def get_channel_map(ip, crate_port):
	# This function gets each active link and tries to map each channel inside to a board QIE number, as assigned by ngccm software.
	channels = []
	links = uhtr_get_active_links(ip_uhtr)
	set_ped_all(crate_port, 31)
	if (len(links) != 6):
		print "ERROR: Not all of the links are active. A channel map can't be identified."
		print ">> The activated links are {0}.".format(links)
	else:
		for n in range(24):
#		for n in [24]:
			n += 1
			print n
			channel = {
				"number": n,
				"link": -1,
				"sublink": -1,
				"targets": [],
			}
			set_ped(crate_port, n, -31)
			for l in links:
				uhtr_read = get_data_from_uhtr(ip, 10, l)
				data = parse_uhtr_raw(uhtr_read["output"])
#				print data["adc"]
				for sl in range(4):
					adc_avg = numpy.mean([i_bx[sl] for i_bx in data["adc"]])
#					print adc_avg
					if (adc_avg == 0):
						channel["targets"].append([l, sl])
			if ( len(channel["targets"]) == 1 ):
				channel["link"] = channel["targets"][0][0]
				channel["sublink"] = channel["targets"][0][1]
			else:
				print "ERROR: The map is not one-to-one!"
				print ">> Checking n = {0} resulted in {1}.".format(n, channel["targets"])
			channels.append(channel)
			set_ped(crate_port, n, 31)
	set_ped_all(crate_port, 6)
	return channels

if __name__ == "__main__":
	name = ""
	if len(sys.argv) == 1:
		name = "bhm"
	elif len(sys.argv) == 2:
		name = sys.argv[1]
	else:
		name = "bhm"
	ts = teststand(name)

	# set unique ID on the FPGA for link mapping
	ngccm.link_test_modeB(ts,1,2,True)
	ngccmLog = ngccm.set_unique_id(ts,1,2)
	uhtr_map = uhtr.map_links(ts.uhtr_ips[0])

	# make sure that the FPGA is in normal readout mode
	ngccm.link_test_modeB(ts,1,2,False)

	ts.set_ped_all(6)
#	set_ped(crate_port, 3, 31)
	links = uhtr.get_links(ts.uhtr_ips[0])
	print "The activated links are {0}.".format(links)
	for link_ in uhtr_map.links :
		if not link_.on : continue
		print "==== Link {0} ====".format( uhtr_map.links.index(link_) )
		link_.Print()
		uhtr_read = uhtr.get_data(ts.uhtr_ips[0], 300, uhtr_map.links.index(link_) )
		data = uhtr.parse_data(uhtr_read["output"])
#		print data["adc"]
		print "Read in {0} bunch crossings.".format(len(data["adc"]))
		for i in range(4):
			print "Channel {0}: ADC_avg = {1:.2f} (sigma = {2:.2f})".format(i, numpy.mean([i_bx[i] for i_bx in data["adc"]]), numpy.std([i_bx[i] for i_bx in data["adc"]]))
